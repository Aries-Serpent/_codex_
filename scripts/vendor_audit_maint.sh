#!/usr/bin/env bash
# =============================================================================
# audit_maintenance.sh
# Purpose: Vendor audit + system reconnaissance (CPU/Mem/Disk/Caches/Network)
# Strategy: Write Python to file and execute (avoids heredoc truncation issues)
# Version: 1.5.4
# =============================================================================
set -Eeuo pipefail

# -----------------------
# Config (overridable)
# -----------------------
export CODEX_FORCE_CPU="${CODEX_FORCE_CPU:-1}"
export CODEX_TORCH_VERSION_BASE="${CODEX_TORCH_VERSION_BASE:-2.8.0}"

export CODEX_ALLOW_TRITON_CPU="${CODEX_ALLOW_TRITON_CPU:-1}"
export CODEX_VENDOR_MAX_PACKAGES="${CODEX_VENDOR_MAX_PACKAGES:-0}"
export CODEX_VENDOR_MAX_SIZE_KB="${CODEX_VENDOR_MAX_SIZE_KB:-0}"
export CODEX_FAIL_ON_VIOLATION="${CODEX_FAIL_ON_VIOLATION:-0}"
export CODEX_VENDOR_LOG_AGG="${CODEX_VENDOR_LOG_AGG:-pre-sync}"
export CODEX_VENDOR_VERBOSE="${CODEX_VENDOR_VERBOSE:-0}"

export CODEX_AUDIT_BOOTSTRAP="${CODEX_AUDIT_BOOTSTRAP:-1}"
export CODEX_OFFLINE="${CODEX_OFFLINE:-0}"

# Recon tunables
export CODEX_NET_TEST_URLS="${CODEX_NET_TEST_URLS:-https://speed.hetzner.de/1MB.bin https://pypi.org/simple/ https://github.com/favicon.ico}"
export CODEX_NET_TRIALS="${CODEX_NET_TRIALS:-3}"
export CODEX_CPU_TRIALS="${CODEX_CPU_TRIALS:-3}"
export CODEX_CPU_TARGET_SECONDS="${CODEX_CPU_TARGET_SECONDS:-1.0}"
export CODEX_CPU_BENCH_BUF_KB="${CODEX_CPU_BENCH_BUF_KB:-8192}"   # default 8 MiB buffer
export CODEX_DISK_BENCH_BYTES="${CODEX_DISK_BENCH_BYTES:-33554432}"  # 32 MiB
export CODEX_DISK_TRIALS="${CODEX_DISK_TRIALS:-2}"

# Error trapping
export CODEX_ERR_TRAP="${CODEX_ERR_TRAP:-1}"

# Locale (stable parsing/printing)
export LC_ALL="${LC_ALL:-C}"

# -----------------------
# Env helpers & sanitization (safe under set -u)
# -----------------------
strip_comment() { local s="${1-}"; printf '%s' "${s%%#*}"; }
# Safe getter for possibly-unset variable by name
get_var() { local name="$1"; eval 'printf %s "${'"$name"'-}"'; }
# Robust "is set?" check without indirect expansion (safe under set -u)
is_defined() { local var="$1"; eval "declare -p $var" >/dev/null 2>&1; }
sanitize_env() {
  local v val
  # booleans (no sampling controls in maintenance)
  for v in CODEX_FORCE_CPU CODEX_ALLOW_TRITON_CPU CODEX_FAIL_ON_VIOLATION CODEX_AUDIT_BOOTSTRAP CODEX_OFFLINE CODEX_VENDOR_VERBOSE CODEX_ERR_TRAP; do
    val="$(strip_comment "$(get_var "$v")")"
    [[ -n "$val" ]] && export "$v"="$val"
  done
  # numeric
  for v in CODEX_VENDOR_MAX_PACKAGES CODEX_VENDOR_MAX_SIZE_KB CODEX_NET_TRIALS CODEX_CPU_TRIALS CODEX_DISK_BENCH_BYTES CODEX_DISK_TRIALS CODEX_CPU_BENCH_BUF_KB; do
    val="$(strip_comment "$(get_var "$v")")"
    [[ -n "$val" ]] && export "$v"="$val"
  done
  # strings
  for v in CODEX_VENDOR_LOG_AGG CODEX_TORCH_VERSION_BASE CODEX_NET_TEST_URLS CODEX_CPU_TARGET_SECONDS; do
    val="$(strip_comment "$(get_var "$v")")"
    [[ -n "$val" ]] && export "$v"="$val"
  done
}
sanitize_env

# -----------------------
# Paths & logging
# -----------------------
REPO_ROOT="${REPO_ROOT:-$(pwd)}"
CACHE_DIR="$REPO_ROOT/.codex/cache"
LOG_DIR="$REPO_ROOT/.codex/logs"
mkdir -p "$CACHE_DIR" "$LOG_DIR" artifacts 2>/dev/null || true

AUDIT_JSON="$CACHE_DIR/vendor_audit.maintenance.json"
ERROR_JSON="$CACHE_DIR/vendor_audit.maintenance.error.json"
PY_FILE="$CACHE_DIR/vendor_audit_maint.py"

log(){ printf "[maint-audit] %s %s\n" "$(date -Iseconds)" "$*"; }
die(){ printf "[maint-audit][ERROR] %s\n" "$*" >&2; exit 1; }
[[ "${CODEX_ERR_TRAP}" == "1" ]] && trap 'ec=$?; [[ $ec -ne 0 ]] && log "ERR ec=%s cmd=%s" "$ec" "${BASH_COMMAND}"' ERR

# venv (best-effort)
if [[ -d "$REPO_ROOT/.venv" ]]; then
  # shellcheck disable=SC1091
  source "$REPO_ROOT/.venv/bin/activate" || log "WARN: Could not activate .venv; continuing with system python"
fi

# uv bootstrap (optional) — parity, will no-op when offline or network-blocked
if [[ "$CODEX_OFFLINE" != "1" && "$CODEX_AUDIT_BOOTSTRAP" == "1" ]]; then
  if ! command -v uv >/dev/null 2>&1; then
    if command -v curl >/dev/null 2>&1; then curl -fsSL https://astral.sh/uv/install.sh | bash || true; fi
    command -v uv >/dev/null 2>&1 || python3 -m pip install --user -q uv || true
    export PATH="$HOME/.local/bin:$PATH"
  fi
fi

# -----------------------
# Python audit (written to file)
# -----------------------
cat >"$PY_FILE" <<'PY'
# -*- coding: utf-8 -*-
import os, sys, json, re, pathlib, tempfile, shutil, subprocess, time, socket, ssl, urllib.request, statistics, platform, traceback
from typing import List, Dict, Any, Tuple, Optional
from importlib import metadata as md
from shutil import which as which_bin

def _clean(s: str) -> str: return (s or "").split('#',1)[0].strip()
def getenv_str(n:str,d:str)->str: return _clean(os.getenv(n,d))
def getenv_int(n:str,d:int)->int:
    raw=getenv_str(n,str(d)); m=re.match(r'^\s*([+-]?\d+)',raw); return int(m.group(1)) if m else d
def getenv_bool(n:str,d:bool)->bool:
    raw=getenv_str(n,'1' if d else '0').lower(); return raw in ('1','true','yes','on')
def run(cmd: List[str], env: Dict[str,str]=None) -> Tuple[int,str]:
    try: out=subprocess.check_output(cmd, env=env, stderr=subprocess.STDOUT, text=True); return 0,out
    except subprocess.CalledProcessError as e: return e.returncode, e.output
def which(cmd:str)->bool: return which_bin(cmd) is not None

REPO_ROOT=pathlib.Path(getenv_str("REPO_ROOT", os.getcwd()))
CACHE_DIR=REPO_ROOT/".codex"/"cache"
LOCK_FILE=REPO_ROOT/"uv.lock"
offline=getenv_bool("CODEX_OFFLINE", False)
force_cpu=getenv_bool("CODEX_FORCE_CPU", True)
bootstrap=getenv_bool("CODEX_AUDIT_BOOTSTRAP", True)
allow_triton=getenv_bool("CODEX_ALLOW_TRITON_CPU", True)
torch_base=getenv_str("CODEX_TORCH_VERSION_BASE","2.8.0")
vendor_log_agg=getenv_str("CODEX_VENDOR_LOG_AGG","pre-sync")
max_pkgs=getenv_int("CODEX_VENDOR_MAX_PACKAGES",0)
max_size_kb=getenv_int("CODEX_VENDOR_MAX_SIZE_KB",0)

# Recon tunables
net_urls=[u for u in getenv_str("CODEX_NET_TEST_URLS","https://speed.hetzner.de/1MB.bin https://pypi.org/simple/ https://github.com/favicon.ico").split() if u]
net_trials=getenv_int("CODEX_NET_TRIALS",3)
cpu_trials=getenv_int("CODEX_CPU_TRIALS",3)
cpu_target=getenv_str("CODEX_CPU_TARGET_SECONDS","1.0")
try: cpu_target=float(cpu_target)
except Exception: cpu_target=1.0
cpu_buf_kb=getenv_int("CODEX_CPU_BENCH_BUF_KB",8192)
disk_bytes=getenv_int("CODEX_DISK_BENCH_BYTES", 32*1024*1024)
disk_trials=getenv_int("CODEX_DISK_TRIALS",2)

# ---------------- Vendor detection & torch bootstrap ----------------
def ensure_torch_for_audit()->Dict[str,Any]:
    meta={"attempted": False, "rc": 0, "note": "", "used":"none"}
    if offline or not bootstrap: meta["note"]="offline or bootstrap disabled"; return meta
    try: import torch; meta["note"]="already present"; return meta
    except Exception: pass
    idx_env=os.environ.copy()
    if force_cpu:
        idx_env["PIP_INDEX_URL"]="https://download.pytorch.org/whl/cpu"
        idx_env["PIP_EXTRA_INDEX_URL"]="https://pypi.org/simple"
    meta["attempted"]=True
    if which("uv"):
        rc,out=run(["uv","pip","install","--python",os.getenv("UV_PYTHON","python"), f"torch=={torch_base}"], env=idx_env); meta["rc"]=rc; meta["used"]="uv"
        if rc!=0: meta["note"]=(out or "")[:800]
    else:
        rc,out=run([sys.executable,"-m","pip","install", f"torch=={torch_base}"], env=idx_env); meta["rc"]=rc; meta["used"]="pip"
        if rc!=0: meta["note"]=(out or "")[:800]
    return meta

def is_vendor_name(name:str)->bool:
    n=name.lower(); return n.startswith("nvidia-") or n in {"triton","torchtriton"}

def vendor_filter(name:str)->bool:
    n=name.lower()
    if allow_triton and n=="triton": return False
    return n.startswith("nvidia-") or n in {"triton","torchtriton"}

def safe_md_distributions():
    try: return list(md.distributions())
    except Exception: return []

def gather_vendor_distributions()->List[Dict[str,Any]]:
    vendors=[]
    for dist in safe_md_distributions():
        try: name=(dist.metadata.get("Name") or dist.metadata.get("name") or "").lower()
        except Exception: continue
        if not is_vendor_name(name): continue
        version=(getattr(dist,"version","") or "").strip()
        files=list(getattr(dist,"files",[]) or [])
        total_bytes=0; roots=set()
        for f in files:
            try:
                p=dist.locate_file(f); roots.add(str(p.parent))
                if p.exists(): total_bytes += p.stat().st_size
            except Exception: continue
        vendors.append({"name":name,"version":version,"total_kb":int(total_bytes/1024),"roots":sorted(roots)[:5]})
    return vendors

def compute_min_max(vendors: List[Dict[str, Any]]) -> Dict[str, Any]:
    f=[v for v in vendors if vendor_filter(v["name"])]
    sizes=[int(v.get("total_kb",0)) for v in f]
    return {"count_total": len(f), "size_total_kb": int(sum(sizes) if sizes else 0), "size_min_kb": int(min(sizes) if sizes else 0), "size_max_kb": int(max(sizes) if sizes else 0)}

def lock_gpu_names()->List[str]:
    if not LOCK_FILE.exists(): return []
    try:
        names=set()
        for m in re.finditer(r'"name"\s*:\s*"([^"]+)"', LOCK_FILE.read_text(), re.I):
            n=m.group(1).lower()
            if is_vendor_name(n): names.add(n)
        return sorted(names)
    except Exception: return []

def sync_log_vendor_events()->Dict[str,int]:
    counts={"nvidia_downloads":0,"triton_downloads":0}
    for p in (CACHE_DIR/"uv_sync.log", CACHE_DIR/"uv_sync_maint.log"):
        if not p.exists(): continue
        try:
            txt=p.read_text()
        except Exception:
            continue
        counts["nvidia_downloads"] += len(re.findall(r"Downloading\s+nvidia-", txt, re.I))
        counts["triton_downloads"] += len(re.findall(r"Downloading\s+triton\b", txt, re.I))
    return counts

def torch_info()->Dict[str,Any]:
    info={"version":"(unknown)","cuda_build":False,"cuda_available":False,"cpu_tag":False,"source":"none"}
    try:
        import torch; v=torch.__version__
        info.update({"version":str(v),"cpu_tag":"+cpu" in str(v),"cuda_build":bool(getattr(getattr(torch,"version",None),"cuda",None)),"cuda_available":bool(getattr(torch,"cuda",None) and torch.cuda.is_available()),"source":"import"})
        return info
    except Exception: pass
    try:
        v=md.version("torch"); info.update({"version":str(v),"cpu_tag":"+cpu" in str(v),"source":"metadata"})
    except Exception: pass
    try:
        if LOCK_FILE.exists():
            m=re.search(r'"name"\s*:\s*"torch".{0,200}?"version"\s*:\s*"([^"]+)"', LOCK_FILE.read_text(), re.I|re.S)
            if m: ver=m.group(1); info["version"]=ver; info["cpu_tag"]="+cpu" in ver; info["source"]=info["source"] if info["source"]!="none" else "lock"
    except Exception: pass
    return info

# ---------------- System Recon & Benchmarks ----------------
def read_first(path:str)->Optional[str]:
    try:
        with open(path,'r') as f: return f.read().strip()
    except Exception: return None

def parse_pressure(path:str)->Optional[Dict[str,Any]]:
    txt=read_first(path)
    if not txt: return None
    out={}
    for line in txt.splitlines():
        parts=line.split()
        if not parts: continue
        lvl=parts[0]
        metrics={}
        for kv in parts[1:]:
            if "=" not in kv: continue
            k,v=kv.split("=",1)
            try: metrics[k]= float(v) if "." in v else int(v)
            except Exception: metrics[k]=v
        out[lvl]=metrics
    return out

def psi_caps()->Dict[str,Any]:
    return {"cpu": parse_pressure("/proc/pressure/cpu"),
            "io": parse_pressure("/proc/pressure/io"),
            "memory": parse_pressure("/proc/pressure/memory")}

def cpu_stat()->Dict[str,Any]:
    st=read_first("/sys/fs/cgroup/cpu.stat")
    out={}
    if st:
        for line in st.splitlines():
            parts=line.strip().split()
            if len(parts)==2:
                k,v=parts
                try: out[k]=int(v)
                except Exception: out[k]=v
    pstat=read_first("/proc/stat")
    if pstat:
        first=pstat.splitlines()[0].split()
        if first and first[0]=="cpu" and len(first)>=9:
            try: out["proc_stat_steal"]=int(first[8])
            except Exception: pass
    return out

def cpu_caps()->Dict[str,Any]:
    caps={"cores_logical": os.cpu_count() or 0, "cores_quota": None, "min_mhz": None, "max_mhz": None, "model": None, "vendor": None, "flags_count": None, "loadavg": None, "cpuset_cpus": None, "cpuset_effective": None, "cpu_shares": None}
    cpu_max=read_first("/sys/fs/cgroup/cpu.max")
    if cpu_max:
        parts=cpu_max.split()
        if len(parts)>=2 and parts[0]!="max":
            try: quota=int(parts[0]); period=int(parts[1]); caps["cores_quota"]=round(quota/period,2)
            except Exception: pass
    caps["cpuset_cpus"]= read_first("/sys/fs/cgroup/cpuset.cpus")
    caps["cpuset_effective"]= read_first("/sys/fs/cgroup/cpuset.cpus.effective")
    try:
        shares=read_first("/sys/fs/cgroup/cpu.weight")
        caps["cpu_shares"]= int(shares) if shares and shares.isdigit() else None
    except Exception: caps["cpu_shares"]= None
    minf=read_first("/sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq")
    maxf=read_first("/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq")
    try: caps["min_mhz"]= int(minf)//1000 if minf and minf.isdigit() else None
    except Exception: pass
    try: caps["max_mhz"]= int(maxf)//1000 if maxf and maxf.isdigit() else None
    except Exception: pass
    try:
        with open("/proc/cpuinfo",'r') as f: txt=f.read()
        m=re.search(r'model name\s*:\s*(.+)', txt); 
        if m: caps["model"]=m.group(1).strip()
        v=re.search(r'vendor_id\s*:\s*([^\n]+)', txt); 
        if v: caps["vendor"]=v.group(1).strip()
        flags=re.search(r'flags\s*:\s*(.+)', txt); 
        if flags: caps["flags_count"]=len(flags.group(1).split())
    except Exception: pass
    try: caps["loadavg"]= os.getloadavg()
    except Exception: caps["loadavg"]= None
    return caps

def mem_caps()->Dict[str,Any]:
    caps={"mem_total_bytes": None, "mem_available_bytes": None, "cgroup_mem_max_bytes": None, "mem_current_bytes": None, "swap_max_bytes": None, "swap_current_bytes": None}
    try:
        with open("/proc/meminfo",'r') as f:
            t=f.read()
            mt=re.search(r'MemTotal:\s+(\d+)\s+kB', t); 
            if mt: caps["mem_total_bytes"]=int(mt.group(1))*1024
            ma=re.search(r'MemAvailable:\s+(\d+)\s+kB', t);
            if ma: caps["mem_available_bytes"]=int(ma.group(1))*1024
    except Exception: pass
    mm=read_first("/sys/fs/cgroup/memory.max")
    if mm and mm!="max":
        try: caps["cgroup_mem_max_bytes"]=int(mm)
        except Exception: pass
    mc=read_first("/sys/fs/cgroup/memory.current")
    if mc:
        try: caps["mem_current_bytes"]=int(mc)
        except Exception: pass
    sm=read_first("/sys/fs/cgroup/memory.swap.max")
    if sm and sm!="max":
        try: caps["swap_max_bytes"]=int(sm)
        except Exception: pass
    sc=read_first("/sys/fs/cgroup/memory.swap.current")
    if sc:
        try: caps["swap_current_bytes"]=int(sc)
        except Exception: pass
    return caps

def disk_caps()->Dict[str,Any]:
    caps={"root_total_bytes": None, "root_used_bytes": None, "root_free_bytes": None, "inode_total": None, "inode_free": None, "schedulers": {}}
    try:
        import shutil as sh
        total, used, free = sh.disk_usage("/")
        caps.update({"root_total_bytes": total, "root_used_bytes": total-free, "root_free_bytes": free})
    except Exception: pass
    try:
        st=os.statvfs("/")
        caps["inode_total"]= int(st.f_files)
        caps["inode_free"]= int(st.f_ffree)
    except Exception: pass
    # IO schedulers (best-effort)
    try:
        sysblk=pathlib.Path("/sys/block")
        for dev in sysblk.iterdir():
            sched=dev/"queue"/"scheduler"
            if sched.exists():
                try:
                    s=sched.read_text().strip()
                    # pick [selected] algorithm if present
                    m=re.search(r'\[([^\]]+)\]', s)
                    caps["schedulers"][dev.name]= m.group(1) if m else s
                except Exception: pass
    except Exception: pass
    return caps

def io_cgroup_caps()->Dict[str,Any]:
    txt=read_first("/sys/fs/cgroup/io.stat")
    out={}
    if txt:
        acc={}
        for line in txt.splitlines():
            parts=line.strip().split()
            if not parts: continue
            dev=parts[0]
            kv={}
            for p in parts[1:]:
                if "=" in p:
                    k,v=p.split("=",1)
                    try: kv[k]=int(v)
                    except Exception: kv[k]=v
            acc[dev]=kv
        out["devices"]=acc
        agg={"rbytes":0,"wbytes":0,"rios":0,"wios":0}
        for kv in acc.values():
            for k in agg.keys():
                if k in kv and isinstance(kv[k], int): agg[k]+=kv[k]
        out["aggregate"]=agg
    return out

def pids_caps()->Dict[str,Any]:
    out={"pids_max": None, "pids_current": None}
    pm=read_first("/sys/fs/cgroup/pids.max")
    pc=read_first("/sys/fs/cgroup/pids.current")
    if pm: out["pids_max"]= pm
    if pc:
        try: out["pids_current"]= int(pc)
        except Exception: out["pids_current"]= pc
    return out

def resolv_conf()->Dict[str,Any]:
    cfg={"nameservers":[], "search": []}
    try:
        with open("/etc/resolv.conf","r") as f:
            for line in f:
                line=line.strip()
                if not line or line.startswith("#"): continue
                if line.startswith("nameserver"):
                    toks=line.split()
                    if len(toks)>=2: cfg["nameservers"].append(toks[1])
                elif line.startswith("search"):
                    toks=line.split()
                    cfg["search"]= toks[1:]
    except Exception: pass
    return cfg

def default_route()->Optional[str]:
    # Parse /proc/net/route; gateway is in hex little-endian
    try:
        with open("/proc/net/route","r") as f:
            for line in f.read().strip().splitlines()[1:]:
                parts=line.split()
                if len(parts)>=8:
                    dest, gateway, flags_hex = parts[1], parts[2], parts[3]
                    flags=int(flags_hex,16)
                    if dest == "00000000" and (flags & 0x2):  # G flag
                        g=int(gateway,16)
                        ip=".".join(map(str, [(g & 0xff), (g>>8)&0xff, (g>>16)&0xff, (g>>24)&0xff]))
                        return ip
    except Exception: pass
    return None

def net_ifaces()->List[Dict[str,Any]]:
    out=[]
    base=pathlib.Path("/sys/class/net")
    try:
        for iface in base.iterdir():
            name=iface.name
            try: mtu=int((iface/"mtu").read_text().strip())
            except Exception: mtu=None
            oper=read_first(str(iface/"operstate"))
            sp=None
            try: sp=int((iface/"speed").read_text().strip())
            except Exception: sp=None
            out.append({"name":name,"mtu":mtu,"operstate":oper,"speed_mbps":sp})
    except Exception: pass
    return out

def tls_info()->Dict[str,Any]:
    paths=ssl.get_default_verify_paths()
    return {
        "cafile": getattr(paths,"cafile",None),
        "capath": getattr(paths,"capath",None),
        "openssl_cafile_env": getattr(paths,"openssl_cafile_env",None),
        "openssl_cafile": getattr(paths,"openssl_cafile",None),
        "openssl_capath_env": getattr(paths,"openssl_capath_env",None),
        "openssl_capath": getattr(paths,"openssl_capath",None)
    }

def net_sysctls()->Dict[str,Any]:
    def read_sys(p): 
        try: 
            with open(p,'r') as f: return f.read().strip()
        except Exception: return None
    return {
        "tcp_congestion_control": read_sys("/proc/sys/net/ipv4/tcp_congestion_control"),
        "somaxconn": read_sys("/proc/sys/net/core/somaxconn"),
        "ip_local_port_range": read_sys("/proc/sys/net/ipv4/ip_local_port_range")
    }

def os_info()->Dict[str,Any]:
    info={"os_release":{}, "kernel": platform.uname()._asdict() if hasattr(platform.uname(),'_asdict') else str(platform.uname()), "dockerenv": os.path.exists("/.dockerenv"), "cgroup_1": None}
    try:
        with open("/etc/os-release","r") as f:
            for line in f:
                if "=" in line:
                    k,v=line.strip().split("=",1)
                    info["os_release"][k]=v.strip('"')
    except Exception: pass
    try:
        with open("/proc/1/cgroup","r") as f:
            info["cgroup_1"]=f.read()
    except Exception: pass
    return info

def cache_sizes()->Dict[str,Any]:
    home=pathlib.Path(os.path.expanduser("~"))
    def dir_size(p: pathlib.Path)->int:
        total=0
        try:
            for root,dirs,files in os.walk(p, topdown=True):
                for fn in files:
                    fp=os.path.join(root,fn)
                    try: total += os.path.getsize(fp)
                    except Exception: pass
        except Exception: pass
        return total
    def pip_cache():
        try:
            rc,out=run([sys.executable,"-m","pip","cache","dir"])
            if rc==0:
                p=pathlib.Path(out.strip().splitlines()[-1].strip())
                return p if p.exists() else None
        except Exception: return None
        cand=home/".cache"/"pip"
        return cand if cand.exists() else None
    uv_cache = home/".cache"/"uv"
    pipc = pip_cache()
    hf_cache = pathlib.Path(os.getenv("HF_HOME", str(REPO_ROOT/".hf_cache")))
    codex_cache = REPO_ROOT/".codex"/"cache"
    apt_cache = pathlib.Path("/var/cache/apt")
    npm_cache = home/".npm"
    cargo_reg = home/".cargo"/"registry"
    cargo_git = home/".cargo"/"git"
    go_mod    = pathlib.Path(os.getenv("GOMODCACHE", os.path.join(os.getenv("GOPATH",""), "pkg","mod"))).expanduser()
    yarn_cache= home/".cache"/"yarn"
    out={"uv_cache_bytes": None, "pip_cache_bytes": None, "hf_cache_bytes": None, "codex_cache_bytes": None,
         "apt_cache_bytes": None, "npm_cache_bytes": None, "cargo_registry_bytes": None, "cargo_git_bytes": None,
         "gomod_cache_bytes": None, "yarn_cache_bytes": None}
    if uv_cache.exists(): out["uv_cache_bytes"]= dir_size(uv_cache)
    if pipc and pipc.exists(): out["pip_cache_bytes"]= dir_size(pipc)
    if hf_cache.exists(): out["hf_cache_bytes"]= dir_size(hf_cache)
    if codex_cache.exists(): out["codex_cache_bytes"]= dir_size(codex_cache)
    if apt_cache.exists(): out["apt_cache_bytes"]= dir_size(apt_cache)
    if npm_cache.exists(): out["npm_cache_bytes"]= dir_size(npm_cache)
    if cargo_reg.exists(): out["cargo_registry_bytes"]= dir_size(cargo_reg)
    if cargo_git.exists(): out["cargo_git_bytes"]= dir_size(cargo_git)
    if go_mod.exists(): out["gomod_cache_bytes"]= dir_size(go_mod)
    if yarn_cache.exists(): out["yarn_cache_bytes"]= dir_size(yarn_cache)
    return out

def tool_versions()->Dict[str,Any]:
    vers={}
    def v(cmd, key):
        try:
            rc,out = run(cmd)
            vers[key] = out.strip().splitlines()[0] if rc==0 else None
        except Exception:
            vers[key] = None
    v([sys.executable,"--version"], "python")
    v(["node","-v"], "node")
    v(["npm","-v"], "npm")
    v(["ruby","-v"], "ruby")
    v(["rustc","-V"], "rust")
    v(["go","version"], "go")
    v(["swift","--version"], "swift")
    v(["php","-v"], "php")
    return vers

def network_trials()->Dict[str,Any]:
    caps={"dns_ok": False, "https_443_ok": False, "http_80_ok": False, "outbound_ip": None, "notes": "", "proxies": {}, "urls": {}, "summary": {}, "ifaces": net_ifaces(), "sysctls": net_sysctls(), "tls": tls_info(), "resolv_conf": resolv_conf(), "route_default": default_route()}
    if offline:
        caps["notes"]="offline mode"; return caps
    for k in ("HTTP_PROXY","HTTPS_PROXY","NO_PROXY","http_proxy","https_proxy","no_proxy","PIP_INDEX_URL","PIP_EXTRA_INDEX_URL"):
        v=os.getenv(k); 
        if v: caps["proxies"][k]=v
    # DNS
    try: socket.getaddrinfo("pypi.org", 443); socket.getaddrinfo("github.com", 443); caps["dns_ok"]=True
    except Exception as e: caps["notes"]+=f"dns_err={str(e)[:120]} "
    # HTTPS/TLS
    try:
        ctx=ssl.create_default_context()
        with socket.create_connection(("pypi.org", 443), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname="pypi.org"): caps["https_443_ok"]= True
    except Exception as e: caps["notes"]+=f"tls_err={str(e)[:120]} "
    # HTTP/80
    try:
        with socket.create_connection(("pypi.org", 80), timeout=5) as _: caps["http_80_ok"]= True
    except Exception as e:
        caps["notes"]+=f"http80_err={str(e)[:80]} "
    # Outbound IP (best-effort)
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=5) as r: caps["outbound_ip"]= r.read().decode("utf-8")[:64]
    except Exception: pass
    # Throughput trials
    def timed_get(url:str, bytes_cap:int=2_000_000)->Optional[float]:
        try:
            start=time.perf_counter()
            with urllib.request.urlopen(url, timeout=15) as r:
                read=0
                while True:
                    chunk=r.read(64*1024)
                    if not chunk: break
                    read += len(chunk)
                    if read >= bytes_cap: break
            dur=time.perf_counter()-start
            if dur<=0: return None
            mbits=(read*8)/(1_000_000)
            return round(mbits/dur,2)
        except Exception:
            return None
    all_speeds=[]
    for url in net_urls:
        speeds=[]
        for _ in range(net_trials):
            sp=timed_get(url)
            if sp is not None:
                speeds.append(sp); all_speeds.append(sp)
        caps["urls"][url]= {"trials": len(speeds), "speeds_mbps": speeds, "min": (min(speeds) if speeds else None), "median": (statistics.median(speeds) if speeds else None), "max": (max(speeds) if speeds else None)}
    if all_speeds:
        caps["summary"]= {"min": min(all_speeds), "median": statistics.median(all_speeds), "max": max(all_speeds)}
    return caps

def cpu_bench()->Dict[str,Any]:
    results=[]
    size=max(cpu_buf_kb*1024, 1024)
    try:
        buf=bytearray(os.urandom(size))
    except Exception:
        buf=bytearray(b"\x00")*1024
    for _ in range(cpu_trials):
        processed=0
        start=time.perf_counter()
        while (time.perf_counter() - start) < float(cpu_target):
            for i in range(len(buf)): buf[i] ^= 0xAA
            processed += len(buf)
        dur=time.perf_counter() - start
        mbps = (processed/ (1024*1024)) / dur if dur>0 else 0.0
        results.append(round(mbps,2))
    return {"trials": len(results), "speeds_MBps": results, "min": (min(results) if results else 0.0), "median": (statistics.median(results) if results else 0.0), "max": (max(results) if results else 0.0)}

def disk_bench()->Dict[str,Any]:
    results={"write_MBps": [], "read_MBps": []}
    tmpf = CACHE_DIR / f"disk_bench_{int(time.time())}.bin"
    data=os.urandom(1024*1024)
    try:
        for _ in range(disk_trials):
            with open(tmpf, "wb") as f:
                start=time.perf_counter()
                left=disk_bytes
                while left>0:
                    n=min(left, len(data)); f.write(data[:n]); left-=n
                f.flush(); os.fsync(f.fileno())
            dur=time.perf_counter()-start
            mbps=(disk_bytes/(1024*1024))/dur if dur>0 else 0.0
            results["write_MBps"].append(round(mbps,2))
        for _ in range(disk_trials):
            with open(tmpf, "rb") as f:
                start=time.perf_counter()
                while f.read(1024*1024): pass
            dur=time.perf_counter()-start
            mbps=(disk_bytes/(1024*1024))/dur if dur>0 else 0.0
            results["read_MBps"].append(round(mbps,2))
    finally:
        try: tmpf.unlink(missing_ok=True)
        except Exception: pass
    def stat(vals): 
        return {"min": (min(vals) if vals else None), "median": (statistics.median(vals) if vals else None), "max": (max(vals) if vals else None)}
    results["write_stats"]=stat(results["write_MBps"])
    results["read_stats"]=stat(results["read_MBps"])
    return results

def verdicts(minmax:Dict[str,Any])->Dict[str,Any]:
    violations=[]
    if max_pkgs >= 0 and minmax["count_total"] > max_pkgs: violations.append(f"vendor package count {minmax['count_total']} > max {max_pkgs}")
    if max_size_kb >= 0 and minmax["size_total_kb"] > max_size_kb: violations.append(f"vendor total size {minmax['size_total_kb']}KB > max {max_size_kb}KB")
    return {"violations": violations, "ok": len(violations) == 0}

def run_audit():
    bootstrap_status=ensure_torch_for_audit()
    vendors=gather_vendor_distributions()
    minmax=compute_min_max(vendors)
    lock_names=lock_gpu_names()
    sync_counts=sync_log_vendor_events()
    tinfo=torch_info()
    net=network_trials()
    cpu=cpu_bench()
    disk=disk_bench()
    mem=mem_caps()
    cpu_caps_v=cpu_caps()
    cpu_stat_v=cpu_stat()
    disk_caps_v=disk_caps()
    psi=psi_caps()
    io_cg=io_cgroup_caps()
    pids=pids_caps()
    caches=cache_sizes()
    tools=tool_versions()
    osinf=os_info()
    limits={"raw": None}
    try:
        with open("/proc/self/limits","r") as f: limits["raw"]=f.read()
    except Exception: pass

    audit={
      "phase":"maintenance",
      "policy":{"allow_triton_cpu":allow_triton,"max_packages":max_pkgs,"max_size_kb":max_size_kb,"vendor_log_agg":vendor_log_agg,"bootstrap":bootstrap,
                "net_trials": net_trials, "cpu_trials": cpu_trials, "cpu_target_s": cpu_target,
                "cpu_buf_kb": cpu_buf_kb, "disk_bytes": disk_bytes, "disk_trials": disk_trials, "net_urls": net_urls},
      "torch": tinfo,
      "bootstrap_status": bootstrap_status,
      "vendors": vendors,
      "minmax_installed": minmax,
      "lock_scan_names": lock_names,
      "sync_vendor_downloads": sync_counts,
      "system_caps": {
          "cpu": cpu_caps_v, "cpu_stat": cpu_stat_v, "memory": mem, "disk": disk_caps_v,
          "psi": psi, "cgroup_io": io_cg, "pids": pids, "caches": caches, "network": net,
          "tools": tools, "os": osinf, "limits": limits
      },
      "bench": {"cpu_MBps": cpu, "disk_MBps": disk},
      "verdict": verdicts(minmax)
    }

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (REPO_ROOT/".codex"/"cache"/"vendor_audit.maintenance.json").write_text(json.dumps(audit, indent=2))

    def fmt_bytes(b):
        if b is None: return "n/a"
        units=["B","KB","MB","GB","TB"]; i=0; x=float(b)
        while x>=1024 and i<len(units)-1: x/=1024; i+=1
        return f"{x:.2f}{units[i]}"

    print("=== Vendor Audit (Maintenance) ===")
    print(f"- Torch: version={tinfo.get('version')} cpu_tag={tinfo.get('cpu_tag')} cuda_available={tinfo.get('cuda_available')} (src={tinfo.get('source')})")
    print(f"- Vendors (installed, filtered): count={minmax['count_total']} total_size_kb={minmax['size_total_kb']} min_kb={minmax['size_min_kb']} max_kb={minmax['size_max_kb']}")
    print(f"- uv.lock GPU refs: {', '.join(lock_names) if lock_names else 'none'}")
    print(f"- Sync vendor downloads: nvidia={sync_counts['nvidia_downloads']} triton={sync_counts['triton_downloads']}")
    print("-- System Capabilities Snapshot --")
    print(f"CPU: cores={cpu_caps_v.get('cores_logical')} quota={cpu_caps_v.get('cores_quota')} bench.mbps(min/med/max)={cpu.get('min')}/{cpu.get('median')}/{cpu.get('max')}")
    print(f"MEM: total={fmt_bytes(mem.get('mem_total_bytes'))} avail={fmt_bytes(mem.get('mem_available_bytes'))} cgroup_max={fmt_bytes(mem.get('cgroup_mem_max_bytes'))}")
    print(f"DISK: total={fmt_bytes(disk_caps_v.get('root_total_bytes'))} free={fmt_bytes(disk_caps_v.get('root_free_bytes'))} "
          f"IO.write/read MBps(min/med/max)={disk['write_stats']['min']}/{disk['write_stats']['median']}/{disk['write_stats']['max']} | "
          f"{disk['read_stats']['min']}/{disk['read_stats']['median']}/{disk['read_stats']['max']}")
    single_speed=None
    urls=net.get("urls",{})
    for url, vals in urls.items():
        if vals.get("speeds_mbps"): single_speed = vals["speeds_mbps"][0]; break
    print(f"NET: dns_ok={net.get('dns_ok')} https_ok={net.get('https_443_ok')} http80_ok={net.get('http_80_ok')} mbps(single)={(single_speed if single_speed is not None else 'n/a')} proxies={bool(net.get('proxies'))}")
    if audit["verdict"]["ok"]:
        print("- Verdict: OK (no vendor policy violations)")
    else:
        print("- Verdict: VIOLATIONS detected:")
        for v in audit["verdict"]["violations"]:
            print(f"  * {v}")

if __name__ == "__main__":
    try:
        run_audit()
    except Exception as e:
        # Persist structured error artifact for diagnostics
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        err={
            "phase":"maintenance",
            "error":{"type": type(e).__name__, "message": str(e), "traceback": traceback.format_exc(limit=2000)},
            "policy":{"allow_triton_cpu":allow_triton,"max_packages":max_pkgs,"max_size_kb":max_size_kb,"vendor_log_agg":vendor_log_agg,"bootstrap":bootstrap,
                      "net_trials": net_trials, "cpu_trials": cpu_trials, "cpu_target_s": cpu_target,
                      "cpu_buf_kb": cpu_buf_kb, "disk_bytes": disk_bytes, "disk_trials": disk_trials, "net_urls": net_urls}
        }
        try:
            (REPO_ROOT/".codex"/"cache"/"vendor_audit.maintenance.error.json").write_text(json.dumps(err, indent=2))
        except Exception:
            pass
        print(f"[MAINT-AUDIT][ERROR] {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(2)
PY

# Execute Python file
python "$PY_FILE" | tee /tmp/vendor_audit_maint.out

# Exit gate
VIOLATIONS=0
if grep -q "VIOLATIONS detected" /tmp/vendor_audit_maint.out; then VIOLATIONS=1; fi
if [[ "${CODEX_FAIL_ON_VIOLATION}" == "1" && $VIOLATIONS -ne 0 ]]; then die "Vendor policy violations in maintenance audit"; fi

log "Maintenance vendor audit complete. JSON: $AUDIT_JSON"

exit 0

