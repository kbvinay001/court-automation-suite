"""Scan all Python files for syntax errors."""
import os, sys

dirs_to_scan = ['backend', 'whatsapp-assistant', 'ml_models', 'tests']
errors = []

for scan_dir in dirs_to_scan:
    if not os.path.isdir(scan_dir):
        continue
    for root, dirs, files in os.walk(scan_dir):
        dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'node_modules', 'n8n')]
        for f in files:
            if f.endswith('.py'):
                path = os.path.join(root, f)
                try:
                    with open(path, 'r', encoding='utf-8') as fh:
                        compile(fh.read(), path, 'exec')
                except SyntaxError as e:
                    errors.append(f'{path}:{e.lineno}: {e.msg}')

if errors:
    print(f'Found {len(errors)} syntax error(s):')
    for e in errors:
        print(f'  {e}')
else:
    print('No syntax errors found in any Python files.')
