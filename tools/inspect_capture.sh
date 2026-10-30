#!/bin/bash
# Read-only checks for a captured demo take. Never modifies the recording.
set -euo pipefail
if [ "$#" -ne 1 ]; then
  echo 'Usage: bash tools/inspect_capture.sh /absolute/path/to/take.mov' >&2
  exit 2
fi
ffprobe -v error -show_entries format=duration,size:stream=index,codec_type,codec_name,width,height,sample_rate,channels -of json "$1"
ffmpeg -hide_banner -i "$1" -vn -af volumedetect -f null - 2>&1 | rg 'mean_volume|max_volume'
