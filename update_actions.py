import os
import re
import glob

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Update actions/checkout
    content = re.sub(r'uses: actions/checkout@(?:v[1-4](?:\.[0-9]+)*|[a-f0-9]{40})', 'uses: actions/checkout@v5', content)
    
    # Update actions/setup-python
    content = re.sub(r'uses: actions/setup-python@(?:v[1-4](?:\.[0-9]+)*|[a-f0-9]{40})', 'uses: actions/setup-python@v6', content)
    
    # Update actions/upload-artifact
    content = re.sub(r'uses: actions/upload-artifact@(?:v[1-4](?:\.[0-9]+)*|[a-f0-9]{40})', 'uses: actions/upload-artifact@v5', content)
    
    # Update actions/download-artifact
    content = re.sub(r'uses: actions/download-artifact@(?:v[1-4](?:\.[0-9]+)*|[a-f0-9]{40})', 'uses: actions/download-artifact@v5', content)
    
    # Update actions/cache
    content = re.sub(r'uses: actions/cache@(?:v[1-4](?:\.[0-9]+)*|[a-f0-9]{40})', 'uses: actions/cache@v5', content)
    content = re.sub(r'uses: actions/cache/restore@(?:v[1-4](?:\.[0-9]+)*|[a-f0-9]{40})', 'uses: actions/cache/restore@v5', content)
    content = re.sub(r'uses: actions/cache/save@(?:v[1-4](?:\.[0-9]+)*|[a-f0-9]{40})', 'uses: actions/cache/save@v5', content)

    # Update actions/github-script
    content = re.sub(r'uses: actions/github-script@(?:v[1-7](?:\.[0-9]+)*|[a-f0-9]{40})', 'uses: actions/github-script@v8', content)

    with open(filepath, 'w') as f:
        f.write(content)

for filepath in glob.glob('.github/workflows/**/*.yml', recursive=True) + glob.glob('.github/workflows/**/*.yaml', recursive=True):
    process_file(filepath)

print("Done updating action versions.")
