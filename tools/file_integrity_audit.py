#!/usr/bin/env python3
import sys, json, hashlib, pathlib, fnmatch

def sha256(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def snap(root):
    out = {}
    for p in root.rglob('*'):
        if p.is_file() and '.git' not in p.parts:
            rel = str(p.relative_to(root))
            out[rel] = {'sha256': sha256(p), 'size': p.stat().st_size}
    return out

def save(path, obj):
    pathlib.Path(path).write_text(json.dumps(obj, indent=2), encoding='utf-8')

def load(path):
    return json.loads(pathlib.Path(path).read_text(encoding='utf-8'))

def match_any(p, patterns):
    return any(fnmatch.fnmatch(p, pat) for pat in patterns)

def compare(pre, post, allow_removed, allow_added):
    pre_map, post_map = load(pre), load(post)
    pre_hash2 = {}
    post_hash2 = {}
    for p, m in pre_map.items():
        pre_hash2.setdefault(m['sha256'], set()).add(p)
    for p, m in post_map.items():
        post_hash2.setdefault(m['sha256'], set()).add(p)
    removed = [p for p in pre_map if p not in post_map]
    added = [p for p in post_map if p not in pre_map]
    changed = [p for p in pre_map if p in post_map and pre_map[p]['sha256'] != post_map[p]['sha256']]
    moves = []
    rem_left = []
    for p in removed:
        tgt = sorted(post_hash2.get(pre_map[p]['sha256'], set()))
        if tgt:
            moves.append({'from': p, 'to': tgt[0]})
        else:
            rem_left.append(p)
    add_left = set(added)
    for m in moves:
        if m['to'] in add_left:
            add_left.remove(m['to'])
    unexpected_removed = [p for p in rem_left if not match_any(p, allow_removed)]
    unexpected_added = [p for p in add_left if not match_any(p, allow_added)]
    ok = not changed and not unexpected_removed and not unexpected_added
    return ok, {
        'summary': {
            'removed': len(removed),
            'added': len(added),
            'changed': len(changed),
            'moves': len(moves),
            'unexpected_removed': len(unexpected_removed),
            'unexpected_added': len(unexpected_added),
        },
        'details': {
            'removed': removed,
            'added': added,
            'changed': changed,
            'moves': moves,
            'unexpected_removed': unexpected_removed,
            'unexpected_added': list(unexpected_added),
        },
    }

def main():
    if len(sys.argv) < 3 or sys.argv[1] not in {'snapshot', 'compare'}:
        print('usage: file_integrity_audit.py snapshot <out.json> | compare <pre.json> <post.json> '
              '[--allow-removed X ...] [--allow-added Y ...]')
        sys.exit(2)
    root = pathlib.Path('.').resolve()
    if sys.argv[1] == 'snapshot':
        save(sys.argv[2], snap(root))
        print(f'[integrity] snapshot -> {sys.argv[2]}')
        return
    allow_removed = []
    allow_added = []
    args = sys.argv[4:]
    i = 0
    while i < len(args):
        if args[i] == '--allow-removed':
            i += 1
            while i < len(args) and not args[i].startswith('--'):
                allow_removed.append(args[i])
                i += 1
            continue
        if args[i] == '--allow-added':
            i += 1
            while i < len(args) and not args[i].startswith('--'):
                allow_added.append(args[i])
                i += 1
            continue
        i += 1
    ok, report = compare(sys.argv[2], sys.argv[3], allow_removed, allow_added)
    print(json.dumps(report, indent=2))
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
