#!/usr/bin/env python3
"""Copy numeric Muse boundary diagnostics from the selected phone. No audio/text."""
import json
import os
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
device = os.environ.get('AYAH_DEVICE_ID')
if not device:
    raise SystemExit('Set AYAH_DEVICE_ID to the approved test phone')
output = root / 'build/logs/phone-muse-diagnostics.json'
output.parent.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, DEVELOPER_DIR='/Applications/Xcode.app/Contents/Developer')
subprocess.run(['xcrun', 'devicectl', '--timeout', '30', 'device', 'copy', 'from',
                '--device', device, '--domain-type', 'appDataContainer',
                '--domain-identifier', 'ai.khirad.apps.ayahlens',
                '--source', 'Library/muse-diagnostics.json', '--destination', str(output)],
               env=env, check=True)
report = json.loads(output.read_text())
print(json.dumps(report, indent=2, sort_keys=True))
