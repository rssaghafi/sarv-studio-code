#!/usr/bin/env bash
# Sarv Studio: does this computer work? Prints OK / FIX lines and changes nothing.
# Run:  bash "$SARV_CODE/scripts/check_setup.sh"   (on Windows: inside WSL)
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODE="${SARV_CODE:-$HERE}"
FAIL=0
ok(){ printf 'OK   %s\n' "$1"; }
bad(){ printf 'FIX  %s\n' "$1"; FAIL=1; }
have(){ command -v "$1" >/dev/null 2>&1; }

echo "Code folder: $CODE"
[ -n "${PERSIAN_STORIES:-}" ] && echo "Project folder (PERSIAN_STORIES): $PERSIAN_STORIES" || echo "Project folder: PERSIAN_STORIES is not set"
echo

if grep -qi microsoft /proc/version 2>/dev/null; then
  ok "running inside WSL (Windows)"
  case "$CODE" in /mnt/*) ok "code folder is on the Windows drive (Claude desktop can connect to it)";; *) echo "NOTE the code folder is inside Linux; Claude desktop will not see it. Keep it under /mnt/c/Users/<you>/Code";; esac
fi

for t in python3 ffmpeg ffprobe node npm git; do have $t && ok "$t found" || bad "$t is missing (see the Setup Guide, part B)"; done
if have python3; then python3 -c 'import sys; sys.exit(0 if sys.version_info>=(3,9) else 1)' && ok "python 3.9 or newer" || bad "python is older than 3.9"; fi
if have node; then [ "$(node -p 'process.versions.node.split(".")[0]')" -ge 18 ] && ok "node 18 or newer" || bad "node is older than 18 (install Node 20 LTS)"; fi

if [ -n "${PERSIAN_STORIES:-}" ] && [ -f "$PERSIAN_STORIES/STUDIO.md" ]; then
  ok "STUDIO.md found in the project folder"
  head -c 200 "$PERSIAN_STORIES/STUDIO.md" >/dev/null 2>&1 && ok "project files are readable (not cloud-only)" || bad "cannot read STUDIO.md: set the folder to 'Always keep on this device' and wait for the sync"
  [ -d "$PERSIAN_STORIES/Films" ] && ok "Films folder present" || bad "Films folder missing: the sync is not finished"
else
  bad "PERSIAN_STORIES must point to the Persian Stories folder (the one that contains STUDIO.md)"
fi

if [ -f "$CODE/.env" ]; then
  ok ".env exists"
  grep -q $'\r' "$CODE/.env" && bad ".env has Windows line endings: open it with nano in WSL and save again, or run: sed -i 's/\\r$//' \"$CODE/.env\""
  for k in FAL_KEY ELEVENLABS_API_KEY; do v="$(grep -E "^$k=" "$CODE/.env" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")"; [ -n "$v" ] && ok "$k is set" || bad "$k is empty in .env"; done
else
  bad ".env is missing: copy .env.example to .env and fill in your own keys"
fi
grep -qE "^SARV_USER=.+" "$CODE/.env" 2>/dev/null && ok "SARV_USER is set" || echo "NOTE SARV_USER is not set in .env: logs default to reza. Edris must set SARV_USER=edris"
[ -d "$CODE/remotion/node_modules" ] && ok "remotion packages installed" || bad "run once:  cd \"$CODE/remotion\" && npm install"
if head -c 200 "$CODE/scripts/render_v03.sh" 2>/dev/null | grep -q $'\r'; then bad "render_v03.sh has Windows line endings: run  git -C \"$CODE\" config core.autocrlf false  then  git -C \"$CODE\" checkout -- ."; else ok "scripts have Unix line endings"; fi

if [ -n "${PERSIAN_STORIES:-}" ] && [ -f "$PERSIAN_STORIES/03_templates/agents/tools/sarv_logs.py" ]; then
  who="$(python3 "$PERSIAN_STORIES/03_templates/agents/tools/sarv_logs.py" whoami 2>/dev/null)"; [ -n "$who" ] && ok "logs will be written as: $who" || bad "sarv_logs.py whoami failed"
fi
echo
[ $FAIL -eq 0 ] && echo "ALL GOOD" || echo "Fix the FIX lines above, then run this again."
exit $FAIL
