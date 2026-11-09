#!/usr/bin/env bash
# pingpong.sh <in.mp4> <out.mp4> [target_seconds=10]  — forward + reversed loop of a locked-camera clip (STUDIO §4: a 5 s wind clip covers up to 10 s).
# Cross-point is a held-frame-free reversal: forward A, reverse A (drops the duplicate end frames), repeat until target, trim.
set -euo pipefail
in=$1; out=$2; tgt=${3:-10}; [ -e "$out" ] && { echo "dest exists: $out" >&2; exit 1; }
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
ffmpeg -v error -y -i "$in" -an -vf "reverse" -c:v libx264 -crf 14 -pix_fmt yuv420p "$tmp/rev.mp4"
ffmpeg -v error -y -i "$in" -an -c:v libx264 -crf 14 -pix_fmt yuv420p "$tmp/fwd.mp4"
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$tmp/fwd.mp4"); n=$(python3 -c "import math;print(max(1,math.ceil($tgt/($d*2))))")
: > "$tmp/l.txt"; for i in $(seq $n); do echo "file '$tmp/fwd.mp4'" >> "$tmp/l.txt"; echo "file '$tmp/rev.mp4'" >> "$tmp/l.txt"; done
ffmpeg -v error -y -f concat -safe 0 -i "$tmp/l.txt" -t "$tgt" -c:v libx264 -crf 16 -pix_fmt yuv420p "$out"
echo "pingpong OK: $out ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out") s)"
