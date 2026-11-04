#!/usr/bin/env python3
"""Compare three synthetic fragments with real Spark only when --live is explicit.

Default: offline preflight. Live use requires spending authorization. No audio is
sent. One diagnostic abstention control deliberately bypasses app eligibility.
Credentials remain in the subprocess environment; results go to ignored build/.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--live', action='store_true')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
output = root / 'build/spark-evaluation'
output.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, DEVELOPER_DIR='/Applications/Xcode.app/Contents/Developer')
if args.live:
    secret = Path.home() / '.secrets/ayah-lens.env'
    for line in secret.read_text().splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            name, value = line.split('=', 1)
            if name.strip() == 'META_API_KEY':
                env['META_API_KEY'] = value.strip().strip('\"\'')
    if not env.get('META_API_KEY'):
        parser.error('Private Meta key is unavailable')
subprocess.run(['xcrun', 'swiftc', '-swift-version', '6', '-O', '-parse-as-library',
                'Core/Sources/AyahLensCore/Recognition.swift',
                'Core/Sources/AyahLensCore/QuranIndex.swift',
                'Core/Sources/AyahLensCore/MuseSpark.swift',
                'tools/evaluate_spark.swift', '-o', str(output / 'evaluate')],
               cwd=root, env=env, check=True)
result = subprocess.run([str(output / 'evaluate')] + (['--live'] if args.live else []),
                        cwd=root, env=env, capture_output=True, text=True, timeout=45)
name = 'live.json' if args.live else 'preflight.json'
try:
    report = json.loads(result.stdout)
except ValueError:
    raise SystemExit('Evaluation failed before a structured result; no output containing credentials was displayed')
(output / name).write_text(json.dumps(report, indent=2) + '\n')
for case in report['cases']:
    print(f"{case['case']}: matcher=abstain, expected={case['expected'] or 'abstain'}, "
          f"Spark={case.get('spark', 'not called')}, seconds={case.get('seconds', 'n/a')}")
print(f'Receipt: build/spark-evaluation/{name}')
raise SystemExit(result.returncode)
