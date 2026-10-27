#!/bin/bash
set -eu
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
python3 tools/generate_project.py
mkdir -p build/logs
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
if [ "${1:-unsigned}" = signed ]; then
  : "${AYAH_DEVICE_ID:?Set AYAH_DEVICE_ID from the connected physical iPhone}"
  destination="platform=iOS,id=$AYAH_DEVICE_ID"
  signing=(-allowProvisioningUpdates -allowProvisioningDeviceRegistration)
elif [ "${1:-unsigned}" = unsigned ]; then
  destination='generic/platform=iOS'
  signing=(CODE_SIGNING_ALLOWED=NO)
else
  echo 'Usage: bash tools/build.sh unsigned|signed' >&2
  exit 2
fi
set +e
xcodebuild -project AyahLens.xcodeproj -scheme AyahLens -configuration Debug \
  -destination "$destination" -derivedDataPath build/DerivedData \
  -clonedSourcePackagesDirPath build/Packages "${signing[@]}" build \
  > build/logs/build.log 2>&1
result=$?
set -e
tail -25 build/logs/build.log
exit "$result"
