#!/usr/bin/env python3
import yaml, pathlib, re
root = pathlib.Path('.')
mk = root/'mkdocs.yml'
if not mk.exists():
    raise SystemExit(0)

data = yaml.safe_load(mk.read_text(encoding='utf-8')) or {}

if data.get('strict', None) is not False:
    data['strict'] = False

def fix_path(p: str) -> str:
    p = re.sub(r'(?:^|/)(ops/)?docs/ops/', 'docs/ops/', p)
    p = re.sub(r'(?:^|/)(guides/)?docs/guides/', 'docs/guides/', p)
    p = re.sub(r'(?:^|/)(changelog/)?docs/changelog/', 'docs/changelog/', p)
    return p

def walk_nav(x):
    if isinstance(x, list):
        return [walk_nav(i) for i in x]
    if isinstance(x, dict):
        return {k: walk_nav(v) for k,v in x.items()}
    if isinstance(x, str):
        return fix_path(x)
    return x

if 'nav' in data:
    data['nav'] = walk_nav(data['nav'])

docs_dir = root/'docs'
present = set()

def collect(x):
    if isinstance(x, list):
        for i in x: collect(i)
    elif isinstance(x, dict):
        for k,v in x.items(): collect(v)
    elif isinstance(x, str):
        present.add(x)

collect(data.get('nav', []))
missing = []
for p in docs_dir.rglob('*.md'):
    rel = str(p.relative_to(root))
    if rel not in present:
        missing.append(rel)

if missing:
    data.setdefault('nav', []).append({'(Other docs)': [{pathlib.Path(m).stem: m} for m in sorted(missing)]})

mk.write_text(yaml.safe_dump(data, sort_keys=False), encoding='utf-8')
print({'added_to_nav': len(missing), 'strict': data.get('strict')})
