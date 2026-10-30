#!/usr/bin/env python3
"""Privately hand a development Meta key to the app for one-time Keychain import.

This does not start a Muse session. Run only after the live-test approval.
The key never appears in arguments, stdout, the app bundle or Git.
"""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()
source = Path.home() / ".secrets/ayah-lens.env"
values = {}
for line in source.read_text().splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        name, value = line.split("=", 1)
        values[name.strip()] = value.strip().strip("\"'")
key = values.get("META_API_KEY", "")
if not key or len(key) > 4096:
    parser.error("META_API_KEY is missing or invalid")
if args.dry_run:
    print("PASS: private Meta key is available for one-time device Keychain import; no device copy or API call occurred")
    raise SystemExit(0)
device = os.environ.get("AYAH_DEVICE_ID")
if not device:
    parser.error("Set AYAH_DEVICE_ID to the approved test phone")
os.environ["DEVELOPER_DIR"] = "/Applications/Xcode.app/Contents/Developer"
bundle = "ai.khirad.apps.ayahlens"
with tempfile.TemporaryDirectory(prefix="ayah-muse-") as temporary:
    handoff = Path(temporary) / "muse-key.once"
    handoff.touch(mode=0o600)
    handoff.write_text(key)
    subprocess.run(["xcrun", "devicectl", "--timeout", "20", "device", "copy", "to",
                    "--device", device, "--domain-type", "appDataContainer", "--domain-identifier", bundle,
                    "--source", str(handoff), "--destination", "Library/muse-key.once"], check=True)
subprocess.run(["xcrun", "devicectl", "--timeout", "20", "device", "process", "launch",
                "--device", device, "--terminate-existing", bundle], check=True)
print("Key handoff copied and app restarted. Confirm Muse access is enabled on the phone. No paid session was started.")
