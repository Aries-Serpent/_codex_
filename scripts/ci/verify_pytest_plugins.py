#!/usr/bin/env python3
"""Verify that pytest plugins are installed and importable."""

import sys


def main():
    plugins = ['pytest_cov', 'xdist', 'pytest_timeout', 'pytest', 'coverage']
    failed = []

    for plugin in plugins:
        try:
            __import__(plugin)
            print(f'  ✓ {plugin}')
        except ImportError as e:
            print(f'  ✗ {plugin}: {e}')
            failed.append(plugin)

    if failed:
        print(f'\n❌ Failed to import: {", ".join(failed)}')
        return 1

    print('\n✅ All pytest plugins verified')
    return 0


if __name__ == '__main__':
    sys.exit(main())
