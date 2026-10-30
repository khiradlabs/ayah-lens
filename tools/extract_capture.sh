#!/bin/bash
# Export one continuous phone-preview interval, retaining the original untouched.
set -euo pipefail
if [ "$#" -ne 4 ]; then
  echo 'Usage: bash tools/extract_capture.sh INPUT START_SECONDS DURATION_SECONDS OUTPUT.mp4' >&2
  exit 2
fi
ffmpeg -hide_banner -loglevel error -n -ss "$2" -i "$1" -t "$3" \
  -vf scale=1080:-2 -r 30 -c:v libx264 -preset fast -crf 18 \
  -pix_fmt yuv420p -c:a aac -b:a 160k "$4"
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height -of json "$4"
