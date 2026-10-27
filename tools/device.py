#!/usr/bin/env python3
"""Install or open the development prototype on an explicitly selected iPhone."""
import argparse
import os
from pathlib import Path
import plistlib
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("action", choices=["install", "launch"])
args = parser.parse_args()
device = os.environ.get("AYAH_DEVICE_ID")
if not device:
    parser.error("Set AYAH_DEVICE_ID from the connected physical iPhone list")
os.environ["DEVELOPER_DIR"] = "/Applications/Xcode.app/Contents/Developer"
root = Path(__file__).resolve().parents[1]
evidence = root / "build/logs"
evidence.mkdir(parents=True, exist_ok=True)
bundle = "ai.khirad.apps.ayahlens"
if args.action == "install":
    app = root / "build/DerivedData/Build/Products/Debug-iphoneos/AyahLens.app"
    profile = plistlib.loads(subprocess.run(
        ["security", "cms", "-D", "-i", str(app / "embedded.mobileprovision")],
        capture_output=True, check=True,
    ).stdout)
    if "65LPT48UNK" not in profile.get("TeamIdentifier", []) or device not in profile.get("ProvisionedDevices", []):
        parser.error("The signed profile does not match the approved team and selected phone")
    subprocess.run(["codesign", "--verify", "--strict", str(app)], check=True)
    command = ["device", "install", "app", "--device", device, str(app)]
else:
    command = ["device", "process", "launch", "--device", device, bundle]
subprocess.run(["xcrun", "devicectl", "--timeout", "30", *command,
                "--json-output", str(evidence / f"{args.action}.json")], check=True)
