#!/bin/sh
# Builds ~/Applications/Animation Dashboard.app (a thin wrapper around dashboard/app.py).
# Needs: the private venv at ~/Library/Application Support/PlanDashboard/venv with pywebview.
# Never deletes anything: it only writes files inside the .app bundle.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
DASH="$(cd "$HERE/.." && pwd)"
VENV="$HOME/Library/Application Support/PlanDashboard/venv"
APP="$HOME/Applications/Animation Dashboard.app"
WORK="${TMPDIR:-/tmp}/plandashboard-icon.$$"

[ -x "$VENV/bin/python" ] || { echo "Missing $VENV (install pywebview first)"; exit 1; }
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources" "$WORK/PlanDashboard.iconset"

# Icon: brand logo (or icon.svg if the logo is missing) -> 1024 PNG -> iconset -> .icns
LOGO="${ICON_SOURCE:-${PERSIAN_STORIES:-$DASH/../../Persian Stories}/01_bible/brand/logo_sarv-simurgh_v2_transparent.png}"
PNG="$WORK/icon.png"
if [ -f "$LOGO" ]; then
  "$VENV/bin/python" "$HERE/make_icon.py" "$LOGO" "$PNG"
else
  echo "Logo not found at $LOGO; using icon.svg"
  qlmanage -t -s 1024 -o "$WORK" "$HERE/icon.svg" >/dev/null 2>&1
  PNG="$WORK/icon.svg.png"
fi
for s in 16 32 128 256 512; do
  sips -z $s $s "$PNG" --out "$WORK/PlanDashboard.iconset/icon_${s}x${s}.png" >/dev/null
  d=$((s * 2)); sips -z $d $d "$PNG" --out "$WORK/PlanDashboard.iconset/icon_${s}x${s}@2x.png" >/dev/null
done
iconutil -c icns "$WORK/PlanDashboard.iconset" -o "$APP/Contents/Resources/PlanDashboard.icns"

cat > "$APP/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>Animation Dashboard</string>
  <key>CFBundleDisplayName</key><string>Animation Dashboard</string>
  <key>CFBundleIdentifier</key><string>studio.sarv.plandashboard</string>
  <key>CFBundleVersion</key><string>1.0</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleExecutable</key><string>PlanDashboard</string>
  <key>CFBundleIconFile</key><string>PlanDashboard</string>
  <key>LSMinimumSystemVersion</key><string>11.0</string>
  <key>NSHighResolutionCapable</key><true/>
</dict></plist>
EOF

# Starter: a tiny compiled program that runs Python in-process (so the Dock shows this app, not "Python")
PYFW_DIR="$(dirname "$("$VENV/bin/python" -c 'import sys; print(sys.base_prefix)' | sed 's|/Python3.framework/.*||')/Python3.framework")"
SITE="$("$VENV/bin/python" -c 'import site; print(site.getsitepackages()[0])')"
clang -O2 -o "$APP/Contents/MacOS/PlanDashboard" "$HERE/launcher.c" \
  -I"$PYFW_DIR/Python3.framework/Headers" -F"$PYFW_DIR" -framework Python3 -Wl,-rpath,"$PYFW_DIR" \
  -DVENV_SITE="\"$SITE\"" -DAPP_PY="\"$DASH/app.py\""
touch "$APP"
echo "Built $APP"
