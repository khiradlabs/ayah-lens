#!/usr/bin/env python3
"""Prepare source-boundary cards for named long-ayah regressions. Default offline.

--live uses Standard Muse Spark, up to three requests, without audio. Existing
valid source-matched plans are reused. Credentials never appear in args or logs.
"""
import argparse
import os
from pathlib import Path
import subprocess
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--live', action='store_true')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
output = root / 'build/phrase-alignments'
output.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, DEVELOPER_DIR='/Applications/Xcode.app/Contents/Developer')
if args.live:
    for line in (Path.home() / '.secrets/ayah-lens.env').read_text().splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            name, value = line.split('=', 1)
            if name.strip() == 'META_API_KEY':
                env['META_API_KEY'] = value.strip().strip('\"\'')
    if not env.get('META_API_KEY'):
        parser.error('Private Meta key is unavailable')
subprocess.run(['xcrun', 'swiftc', '-swift-version', '6', '-O', '-parse-as-library',
                'Core/Sources/AyahLensCore/Recognition.swift',
                'Core/Sources/AyahLensCore/VersePagination.swift',
                'Core/Sources/AyahLensCore/RecitationPortions.swift',
                'Core/Sources/AyahLensCore/MuseSpark.swift',
                'Core/Sources/AyahLensCore/MusePhraseAlignment.swift',
                'tools/prepare_phrase_alignments.swift', '-o', str(output / 'prepare')], cwd=root, env=env, check=True)
result = subprocess.run([str(output / 'prepare')] + (['--live'] if args.live else []), cwd=root, env=env, capture_output=True, text=True, timeout=120)
(output / ('live.log' if args.live else 'preflight.log')).write_text(result.stdout + result.stderr)
print(result.stdout.strip())
if result.returncode:
    raise SystemExit('Preparation failed; private diagnostic receipt retained without displaying credential-bearing errors')
