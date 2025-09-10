#!/usr/bin/env python3
import fnmatch
import hashlib
import json
import pathlib
import subprocess
import sys


def sha256(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''): h.update(chunk)
    return h.hexdigest()

def snapshot(out_path: str):
    root = pathlib.Path('.').resolve()
    out = {}
    for p in root.rglob('*'):
        if p.is_file() and '.git' not in p.parts:
            rel = str(p.relative_to(root))
            out[rel] = {'sha256': sha256(p), 'size': p.stat().st_size}
    pathlib.Path(out_path).write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(f"[integrity] snapshot -> {out_path}")

def compare(pre_path: str, post_path: str, allow_removed: list, allow_added: list) -> int:
    pre = json.loads(pathlib.Path(pre_path).read_text(encoding='utf-8'))
    post = json.loads(pathlib.Path(post_path).read_text(encoding='utf-8'))

    pre_files, post_files = set(pre.keys()), set(post.keys())
    added = list(post_files - pre_files)
    removed = list(pre_files - post_files)
    changed = [p for p in (pre_files & post_files) if pre[p]['sha256'] != post[p]['sha256']]

    post_hash_to_paths = {}
    for pth, meta in post.items():
        post_hash_to_paths.setdefault(meta['sha256'], set()).add(pth)
    moves = []
    rem_left = []
    for rf in removed:
        h = pre[rf]['sha256']
        targets = sorted(post_hash_to_paths.get(h, []))
        if targets:
            moves.append({'from': rf, 'to': targets[0]})
        else:
            rem_left.append(rf)

    add_left = set(added)
    for m in moves:
        if m['to'] in add_left:
            add_left.remove(m['to'])

    def match_any(path, patterns):
        return any(fnmatch.fnmatch(path, pat) for pat in patterns)
    unexpected_removed = [p for p in rem_left if not match_any(p, allow_removed)]
    unexpected_added = [p for p in add_left if not match_any(p, allow_added)]

    try:
        git_renames = subprocess.run([
            'git','diff','--name-status','-M','-C','HEAD~1','HEAD'
        ], capture_output=True, text=True, check=False).stdout.strip()
    except Exception:
        git_renames = ''

    report = {
        'summary': {
            'removed': len(removed), 'added': len(added), 'changed': len(changed),
            'moves': len(moves),
            'unexpected_removed': len(unexpected_removed), 'unexpected_added': len(unexpected_added)
        },
        'details': {
            'removed': removed, 'added': added, 'changed': changed,
            'moves': moves,
            'unexpected_removed': unexpected_removed,
            'unexpected_added': list(add_left),
            'git_diff_name_status': git_renames
        }
    }
    out = pathlib.Path('.')/'.codex'/'validation'/pathlib.Path(pre_path).parent.name/'compare_report.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0 if not changed and not unexpected_removed and not unexpected_added else 1

def main():
    if len(sys.argv) < 3 or sys.argv[1] not in {'snapshot','compare'}:
        print('usage: file_integrity_audit.py snapshot <out.json> | compare <pre.json> <post.json> [--allow-removed X ...] [--allow-added Y ...]')
        return 2
    if sys.argv[1] == 'snapshot':
        snapshot(sys.argv[2]); return 0
    pre, post = sys.argv[2], sys.argv[3]
    allow_removed, allow_added = [], []
    i = 4
    while i < len(sys.argv):
        if sys.argv[i] == '--allow-removed':
            i += 1
            while i < len(sys.argv) and not sys.argv[i].startswith('--'):
                allow_removed.append(sys.argv[i]); i += 1
            continue
        if sys.argv[i] == '--allow-added':
            i += 1
            while i < len(sys.argv) and not sys.argv[i].startswith('--'):
                allow_added.append(sys.argv[i]); i += 1
            continue
        i += 1
    return compare(pre, post, allow_removed, allow_added)

if __name__ == '__main__':
    raise SystemExit(main())
