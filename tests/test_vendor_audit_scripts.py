#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
# 
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
# 
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
# import os
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
# from pathlib import Path
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
# import pytest
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
# if os.getenv("RUN_VENDOR_AUDIT_TESTS", "0") != "1":
#     pytest.skip("vendor audit scripts require RUN_VENDOR_AUDIT_TESTS=1", allow_module_level=True)
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
# REPO_ROOT = Path(__file__).resolve().parents[1]
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
# 
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
#     entries = ",\n".join(
#         f'    {{"name": "{name}", "version": "0.{idx}.0"}}'
#         for idx, name in enumerate(package_names)
#     )
#     content = '{\n  "package": [\n' + entries + "\n  ]\n}\n"
#     (repo_root / "uv.lock").write_text(content, encoding="utf-8")
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
# 
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
#     env = os.environ.copy()
#     env.update(
#         {
#             "REPO_ROOT": str(tmp_path),
#             "CODEX_VENDOR_MAX_PACKAGES": extra_env.get("CODEX_VENDOR_MAX_PACKAGES", "0"),
#             "CODEX_VENDOR_MAX_SIZE_KB": extra_env.get("CODEX_VENDOR_MAX_SIZE_KB", "0"),
#             "CODEX_FAIL_ON_VIOLATION": extra_env.get("CODEX_FAIL_ON_VIOLATION", "0"),
#         }
#     )
#     env.update(extra_env)
#     result = subprocess.run(
#         ["bash", str(REPO_ROOT / "scripts" / script_name)],
#         cwd=REPO_ROOT,
#         env=env,
#         check=False,
#         capture_output=True,
#         text=True,
#     )
#     if result.returncode != 0:
#         raise AssertionError(
#             f"{script_name} failed with code {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
#         )
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
# 
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
#     cache_path = tmp_path / ".codex" / "cache" / filename
#     return json.loads(cache_path.read_text(encoding="utf-8"))
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
# 
# @pytest.mark.usefixtures("tmp_path")
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
#     """Setup audit should honour comment-stripped tunables and persist GPU lock matches."""
#     _write_uv_lock(tmp_path, ["torch", "nvidia-cublas-cu12"])
# 
#     _run_audit(
#     _run_audit(
#         "vendor_audit_setup.sh",
#         tmp_path,
#         {
#             "CODEX_OFFLINE": "1",
#             "CODEX_AUDIT_BOOTSTRAP": "0",
#             "CODEX_CPU_TRIALS": "1",
#             "CODEX_CPU_TARGET_SECONDS": "0.05  # keep run fast",
#             "CODEX_DISK_TRIALS": "1",
#             "CODEX_DISK_BENCH_BYTES": "65536",
#             "CODEX_NET_TRIALS": "1",
#             "CODEX_NET_TEST_URLS": "https://speed.hetzner.de/100KB.bin  # inline note",
#         },
#     )
#     data = _load_cached_json(tmp_path, "vendor_audit.setup.json")
#     assert data["phase"] == "setup", "Data must not be empty"
#     assert data["policy"]["cpu_trials"] == 1, "Data must not be empty"
#     assert data["policy"]["disk_trials"] == 1, "Data must not be empty"
#     assert data["policy"]["disk_bytes"] == 65536, "Data must not be empty"
#     assert data["policy"]["net_trials"] == 1, "Data must not be empty"
#     assert data["policy"]["net_urls"] == ["https://speed.hetzner.de/100KB.bin"], "Data must not be empty"
#     assert data["policy"]["cpu_target_s"] == pytest.approx(0.05, rel=1e-3)
#     assert "nvidia-cublas-cu12" in data["lock_scan_names"], "Data must not be empty"
#     assert data["system_caps"]["network"]["notes"] == "offline mode", "Data must not be empty"
#         hardware = data["system_caps"]["hardware"]
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
# 
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
#     """CODEX_VENDOR_AUDIT_* overrides should drive runtime tunables for setup audits."""
#     _write_uv_lock(tmp_path, ["torch", "triton"])
# 
#     _run_audit(
#     _run_audit(
#         "vendor_audit_setup.sh",
#         tmp_path,
#         {
#             "CODEX_OFFLINE": "0",
#             "CODEX_AUDIT_BOOTSTRAP": "1",
#             "CODEX_CPU_TRIALS": "5",
#             "CODEX_CPU_BENCH_BUF_KB": "4096",
#             "CODEX_DISK_TRIALS": "4",
#             "CODEX_DISK_BENCH_BYTES": "262144",
#             "CODEX_NET_TRIALS": "3",
#             "CODEX_VENDOR_AUDIT_OFFLINE": "1",
#             "CODEX_VENDOR_AUDIT_BOOTSTRAP": "0",
#             "CODEX_VENDOR_AUDIT_CPU_TRIALS": "2",
#             "CODEX_VENDOR_AUDIT_CPU_TARGET_SECONDS": "0.02",
#             "CODEX_VENDOR_AUDIT_CPU_BUFFER_KB": "128",
#             "CODEX_VENDOR_AUDIT_DISK_TRIALS": "1",
#             "CODEX_VENDOR_AUDIT_DISK_BYTES": "65536",
#             "CODEX_VENDOR_AUDIT_NET_TRIALS": "1",
#             "CODEX_VENDOR_AUDIT_NET_URLS": "https://example.invalid/blob.bin",
#         },
#     )
#     data = _load_cached_json(tmp_path, "vendor_audit.setup.json")
#     assert data["policy"]["cpu_trials"] == 2, "Data must not be empty"
#     assert data["policy"]["cpu_target_s"] == pytest.approx(0.02, rel=1e-3)
#     assert data["policy"]["cpu_buf_kb"] == 128, "Data must not be empty"
#     assert data["policy"]["disk_trials"] == 1, "Data must not be empty"
#     assert data["policy"]["disk_bytes"] == 65536, "Data must not be empty"
#     assert data["policy"]["net_trials"] == 1, "Data must not be empty"
#     assert data["policy"]["net_urls"] == ["https://example.invalid/blob.bin"], "Data must not be empty"
#     assert data["system_caps"]["network"]["notes"] == "offline mode", "Data must not be empty"
#     assert not data["bootstrap_status"]["attempted"], "Data must not be empty"
#         hardware = data["system_caps"]["hardware"]
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
# 
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
#     """Maintenance audit should also respect the integration override variables."""
#     _write_uv_lock(tmp_path, ["torch", "nvidia-cufft-cu12"])
# 
#     _run_audit(
#     _run_audit(
#         "vendor_audit_maint.sh",
#         tmp_path,
#         {
#             "CODEX_OFFLINE": "0",
#             "CODEX_AUDIT_BOOTSTRAP": "1",
#             "CODEX_CPU_TRIALS": "4",
#             "CODEX_CPU_BENCH_BUF_KB": "4096",
#             "CODEX_DISK_TRIALS": "3",
#             "CODEX_DISK_BENCH_BYTES": "262144",
#             "CODEX_NET_TRIALS": "2",
#             "CODEX_VENDOR_AUDIT_OFFLINE": "1",
#             "CODEX_VENDOR_AUDIT_BOOTSTRAP": "0",
#             "CODEX_VENDOR_AUDIT_CPU_TRIALS": "3",
#             "CODEX_VENDOR_AUDIT_CPU_TARGET_SECONDS": "0.015",
#             "CODEX_VENDOR_AUDIT_CPU_BUFFER_KB": "192",
#             "CODEX_VENDOR_AUDIT_DISK_TRIALS": "2",
#             "CODEX_VENDOR_AUDIT_DISK_BYTES": "98304",
#             "CODEX_VENDOR_AUDIT_NET_TRIALS": "1",
#             "CODEX_VENDOR_AUDIT_NET_URLS": "https://example.invalid/maint.bin",
#         },
#     )
#     data = _load_cached_json(tmp_path, "vendor_audit.maintenance.json")
#     assert data["phase"] == "maintenance", "Data must not be empty"
#     assert data["policy"]["cpu_trials"] == 3, "Data must not be empty"
#     assert data["policy"]["cpu_target_s"] == pytest.approx(0.015, rel=1e-3)
#     assert data["policy"]["cpu_buf_kb"] == 192, "Data must not be empty"
#     assert data["policy"]["disk_trials"] == 2, "Data must not be empty"
#     assert data["policy"]["disk_bytes"] == 98304, "Data must not be empty"
#     assert data["policy"]["net_trials"] == 1, "Data must not be empty"
#     assert data["policy"]["net_urls"] == ["https://example.invalid/maint.bin"], "Data must not be empty"
#     assert data["system_caps"]["network"]["notes"] == "offline mode", "Data must not be empty"
#     assert not data["bootstrap_status"]["attempted"], "Data must not be empty"
#     assert "nvidia-cufft-cu12" in data["lock_scan_names"], "Data must not be empty"
#         hardware = data["system_caps"]["hardware"]
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
# 
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
#     """Run both vendor audits with higher trial counts and assert rich telemetry."""
#     cpu_trials = 4
#     disk_trials = 3
#     disk_bytes = 131072
#     target_seconds = 0.02
# 
#     _write_uv_lock(tmp_path, [])
# 
#     stress_env = {
#     stress_env = {
#         "CODEX_OFFLINE": "1",
#         "CODEX_AUDIT_BOOTSTRAP": "0",
#         "CODEX_CPU_TRIALS": str(cpu_trials),
#         "CODEX_CPU_TARGET_SECONDS": str(target_seconds),
#         "CODEX_CPU_BENCH_BUF_KB": "256",
#         "CODEX_DISK_TRIALS": str(disk_trials),
#         "CODEX_DISK_BENCH_BYTES": str(disk_bytes),
#         "CODEX_NET_TRIALS": "1",
#         "CODEX_VENDOR_VERBOSE": "1",
#         "CODEX_FAIL_ON_VIOLATION": "1",
#     }
#     _run_audit("vendor_audit_setup.sh", tmp_path, stress_env)
#     _run_audit("vendor_audit_maint.sh", tmp_path, stress_env)
# 
#     setup = _load_cached_json(tmp_path, "vendor_audit.setup.json")
#     maintenance = _load_cached_json(tmp_path, "vendor_audit.maintenance.json")
# 
#     assert setup["phase"] == "setup", "Condition must be true"
#     assert maintenance["phase"] == "maintenance", "Condition must be true"
# 
#     def _assert_phase_metrics(data: dict) -> None:
#         policy = data["policy"]
#         assert policy["cpu_trials"] == cpu_trials, "Condition must be true"
#         assert policy["disk_trials"] == disk_trials, "Condition must be true"
#         assert policy["disk_bytes"] == disk_bytes, "Condition must be true"
#         assert policy["net_trials"] == 1, "Condition must be true"
#         assert "https://speed.hetzner.de/1MB.bin" in policy["net_urls"], "Condition must be true"
#         assert policy["cpu_target_s"] == pytest.approx(target_seconds, rel=1e-3)
# 
#         bench = data["bench"]
#         cpu_bench = bench["cpu_MBps"]
#         assert cpu_bench["trials"] == cpu_trials, "Condition must be true"
#         assert len(cpu_bench["speeds_MBps"]) == cpu_trials, "Collection must not be empty"
#         assert cpu_bench["min"] <= cpu_bench["median"] <= cpu_bench["max"], "Condition must be true"
#         assert all(value > 0 for value in cpu_bench["speeds_MBps"]), "value must be greater than zero"
# 
#         disk_bench = bench["disk_MBps"]
#         assert len(disk_bench["write_MBps"]) == disk_trials, "Collection must not be empty"
#         assert len(disk_bench["read_MBps"]) == disk_trials, "Collection must not be empty"
#         for stats in (disk_bench["write_stats"], disk_bench["read_stats"]):
#             assert stats["min"] <= stats["median"] <= stats["max"], "Condition must be true"
#             assert stats["max"] > 0, "Value must be greater than zero"
# 
#         verdict = data["verdict"]
#         assert verdict["ok"], "Condition must be true"
#         assert verdict["violations"] == [], "Condition must be true"
# 
#         sync = data["sync_vendor_downloads"]
#         assert sync["nvidia_downloads"] == 0, "Condition must be true"
#         assert sync["triton_downloads"] == 0, "Condition must be true"
# 
#         minmax = data["minmax_installed"]
#         assert minmax["count_total"] == 0, "Count must be greater than zero"
#         assert minmax["size_total_kb"] == 0, "Condition must be true"
# 
#         assert data["lock_scan_names"] == [], "Data must not be empty"
# 
#         torch = data["torch"]
#         assert torch["source"] == "none", "t is not valid"
#         assert torch["cuda_available"] is False, "t is not valid"
# 
#         network = data["system_caps"]["network"]
#         assert network["notes"] == "offline mode", "netw is not valid"
#         assert network["dns_ok"] is False, "netw is not valid"
#         assert network["https_443_ok"] is False, "netw is not valid"
#         assert network["http_80_ok"] is False, "netw is not valid"
# 
#         cpu_caps = data["system_caps"]["cpu"]
#         assert cpu_caps["cores_logical"] >= 1, "Value must be greater than zero"
#         assert cpu_caps["cores_quota"] > 0, "Value must be greater than zero"
# 
#         memory = data["system_caps"]["memory"]
#         assert memory["mem_total_bytes"] > 0, "mem must be greater than zero"
# 
#         disk_caps = data["system_caps"]["disk"]
#         assert disk_caps["root_total_bytes"] > 0, "Value must be greater than zero"
#         assert disk_caps["root_free_bytes"] >= 0, "Value must be greater than zero"
# 
#         hardware = data["system_caps"]["hardware"]
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
#         assert set(hardware.keys()) >= {, "Value must be greater than zero"
#             "system",
#             "board",
#             "chassis",
#             "bios",
#             "disks",
#             "nics",
#             "virtualization",
#         }
#         system_hw = hardware["system"]
#         assert isinstance(system_hw, dict)
#         for field in ("brand", "model", "sku", "serial", "uuid"):
#             assert field in system_hw, "Condition must be true"
# 
#         board_hw = hardware["board"]
#         assert isinstance(board_hw, dict)
#         for field in ("brand", "model", "version", "serial", "asset_tag"):
#             assert field in board_hw, "Condition must be true"
# 
#         chassis_hw = hardware["chassis"]
#         assert isinstance(chassis_hw, dict)
#         for field in ("brand", "type", "serial", "version", "asset_tag"):
#             assert field in chassis_hw, "Condition must be true"
# 
#         bios_hw = hardware["bios"]
#         assert isinstance(bios_hw, dict)
#         for field in ("brand", "version", "date"):
#             assert field in bios_hw, "Condition must be true"
# 
#         disks = hardware["disks"]
#         assert isinstance(disks, list)
#         for disk in disks:
#             for field in ("name", "brand", "model", "serial", "size_bytes", "type", "bus", "rota"):
#                 assert field in disk, "Condition must be true"
# 
#         nics = hardware["nics"]
#         assert isinstance(nics, list)
#         for nic in nics:
#             assert "name" in nic, "Condition must be true"
#             assert "operstate" in nic, "Condition must be true"
#             assert "mtu" in nic, "Condition must be true"
#             assert "speed_mbps" in nic, "Condition must be true"
#             assert "mac_address" in nic or nic["name"] == "lo", "Condition must be true"
#             assert "bus_path" in nic or nic["name"] == "lo", "Condition must be true"
#             assert "vendor_id" in nic or nic["name"] == "lo", "Condition must be true"
#             assert "device_id" in nic or nic["name"] == "lo", "Condition must be true"
# 
#         virtualization = hardware["virtualization"]
#         assert set(virtualization.keys()) >= {"systemd_detect_virt", "hypervisor_cpu_flag"}
# 
#     _assert_phase_metrics(setup)
#     _assert_phase_metrics(maintenance)
