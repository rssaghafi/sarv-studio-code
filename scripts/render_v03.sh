#!/usr/bin/env bash
# sarv-render v0.1 — resumable Remotion renders for the Cowork VM.
# Why: each VM call is capped (~180 s) and background jobs die when a call ends, so a render
# is a job of short steps:  setup -> init -> step (repeat until VIDEO DONE) -> finish.
# All build files live in the VM home ($WORK); only the finished file is copied into a connected folder.
#   render_v03.sh setup
#   render_v03.sh init   <job> <composition> <public_dir> <dest.mp4> [props.json]
#   render_v03.sh step   <job>          # renders chunks for ~STEP_BUDGET_S seconds, then exits
#   render_v03.sh finish <job>          # audio pass, concat, mux, loudness report, copy to dest
#   render_v03.sh status <job> | clean <job>
set -euo pipefail
export NODE_USE_ENV_PROXY=1                       # Node must use the VM proxy (else DNS fails)
CODE="${SARV_CODE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"   # the folder this script lives in
SRC="${REMOTION_SRC:-$CODE/remotion}"             # Remotion project source
WORK="${SARV_WORK:-$HOME/sarv-render}"            # node_modules, bundles, chunks: never in connected folders
BUDGET="${STEP_BUDGET_S:-110}"
CHUNK="${CHUNK_FRAMES:-300}"
P="$WORK/proj"; die(){ echo "ERROR: $*" >&2; exit 1; }
jobdir(){ J="$WORK/jobs/$1"; [ -f "$J/job.env" ] || die "no job '$1' (run init)"; . "$J/job.env"; }

case "${1:-}" in
setup)
  mkdir -p "$P" "$WORK/jobs"
  rsync -a --delete --exclude node_modules --exclude out --exclude public --exclude build "$SRC/" "$P/"
  cd "$P"; [ -d node_modules/remotion ] || npm install --no-audit --no-fund --loglevel=error
  npx remotion browser ensure >/dev/null && echo "setup OK: $P ($(node -p "require('remotion/package.json').version"))" ;;
init)
  [ $# -ge 5 ] || die "usage: init <job> <composition> <public_dir> <dest.mp4> [props.json]"
  job=$2 comp=$3 pub=$4 dest=$5 props=${6:-}; [ -d "$P/node_modules" ] || die "run setup first"
  [ -d "$pub" ] || die "public dir not found: $pub"; [ -e "$dest" ] && die "dest exists (never overwrite; bump the version): $dest"
  J="$WORK/jobs/$job"; rm -rf "$J"; mkdir -p "$J/chunks"
  if [ -n "$props" ]; then cp "$props" "$J/props.json"; else echo '{}' > "$J/props.json"; fi
  cd "$P"; npx remotion bundle src/index.ts --public-dir="$pub" --out-dir="$J/bundle" --log=error >/dev/null
  read -r frames fps < <(node -e '
    const {selectComposition}=require("@remotion/renderer");
    selectComposition({serveUrl:process.argv[1],id:process.argv[2],inputProps:require(process.argv[3]),logLevel:"error"})
      .then(c=>console.log(c.durationInFrames,c.fps)).catch(e=>{console.error(e.message);process.exit(1)})' "$J/bundle" "$comp" "$J/props.json")
  n=$(( (frames + CHUNK - 1) / CHUNK ))
  printf 'COMP=%q\nDEST=%q\nFRAMES=%s\nFPS=%s\nN=%s\nCH=%s\n' "$comp" "$dest" "$frames" "$fps" "$n" "$CHUNK" > "$J/job.env"
  echo "init OK: $comp, $frames frames @ ${fps} fps ($(( frames / fps )) s) -> $n chunks of $CHUNK. Next: step $job" ;;
step)
  jobdir "$2"; t0=$(date +%s); last=0; done_n=0
  for i in $(seq 0 $((N-1))); do
    f="$J/chunks/$(printf %04d $i).mp4"; [ -f "$f" ] && { done_n=$((done_n+1)); continue; }
    el=$(( $(date +%s) - t0 )); [ $last -gt 0 ] && [ $(( el + last * 3 / 2 )) -gt "$BUDGET" ] && break
    a=$(( i * CH )); b=$(( a + CH - 1 )); [ $b -ge $FRAMES ] && b=$((FRAMES-1)); s=$(date +%s)
    npx --prefix "$P" remotion render "$J/bundle" "$COMP" "$J/chunks/part.mp4" --frames=$a-$b --muted \
      --props="$J/props.json" --concurrency=${CONC:-4} --scale=${SCALE:-1} --jpeg-quality=${JQ:-80} --log=error >/dev/null
    mv "$J/chunks/part.mp4" "$f"; last=$(( $(date +%s) - s )); done_n=$((done_n+1))
    echo "chunk $((i+1))/$N frames $a-$b: ${last}s"
  done
  [ $done_n -ge $N ] && echo "VIDEO DONE. Next: finish $2" || echo "PROGRESS $done_n/$N. Run: step $2 again" ;;
finish)
  jobdir "$2"; [ "$(ls "$J/chunks"/[0-9]*.mp4 | wc -l)" -ge "$N" ] || die "chunks missing: run step $2"
  [ -e "$DEST" ] && die "dest exists: $DEST"
  ( cd "$J/chunks"; for f in [0-9]*.mp4; do echo "file '$PWD/$f'"; done ) > "$J/list.txt"
  ffmpeg -v error -y -f concat -safe 0 -i "$J/list.txt" -c copy "$J/video.mp4"
  npx --prefix "$P" remotion render "$J/bundle" "$COMP" "$J/audio.wav" --codec=wav --props="$J/props.json" --log=error >/dev/null 2>&1 \
    && ffmpeg -v error -y -i "$J/video.mp4" -i "$J/audio.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest "$J/final.mp4" \
    || { [ "${ALLOW_SILENT:-0}" = 1 ] || die "AUDIO RENDER OR MUX FAILED: no film saved. If this composition is meant to be silent, rerun with ALLOW_SILENT=1"; echo "silent composition (ALLOW_SILENT=1)"; cp "$J/video.mp4" "$J/final.mp4"; }   # v0.3 (Nov 3): never ship a silent film by accident
  if [ "${NORM:-1}" = 1 ] && ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$J/final.mp4" | grep -q .; then
    ffmpeg -v error -y -i "$J/final.mp4" -c:v copy -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:a aac -b:a 320k "$J/final_n.mp4" && mv "$J/final_n.mp4" "$J/final.mp4"
  fi   # v0.2: normalise to -16 LUFS integrated (STUDIO §5); NORM=0 to skip
  lufs=$(ffmpeg -nostats -i "$J/final.mp4" -af ebur128 -f null - 2>&1 | awk '/I:/{v=$2} END{print v}')
  mkdir -p "$(dirname "$DEST")"; cp "$J/final.mp4" "$DEST"
  echo "DONE: $DEST  $(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate:format=duration -of csv=p=0 "$DEST" | tr '\n' ' ') loudness ${lufs:-n/a} LUFS (target -16)" ;;
status) jobdir "$2"; echo "$COMP: $(ls "$J/chunks"/[0-9]*.mp4 2>/dev/null | wc -l)/$N chunks -> $DEST" ;;
clean)  rm -rf "$WORK/jobs/${2:?job}"; echo "cleaned $2 (VM home only)" ;;
*) sed -n 2,11p "$0"; exit 1 ;;
esac
