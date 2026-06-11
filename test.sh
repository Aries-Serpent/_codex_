python3 -c "
            import json, os, textwrap
            code = '''
            try:
                print('success')
            except Exception as exc:
                print(f'Warning: {exc}')
            '''
            exec(textwrap.dedent(code))
"
