"""Animation Dashboard as a Mac window (pywebview). Read-only on the project folders, same as server.py.
Run:  python3 app.py [--root "/path/to/Persian Stories"] [--icon PlanDashboard.icns]
Starts server.py on a free 127.0.0.1 port and shows index.html in its own window.
Task links (target="_blank") open in the default browser, not inside the app.
"""
import argparse, os, sys, threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import server  # noqa: E402
import webview  # noqa: E402

APP_NAME = 'Animation Dashboard'


def dock_identity(icon):
    """Show APP_NAME and its icon in the Dock and menu bar instead of 'Python'."""
    try:
        from Foundation import NSBundle
        from AppKit import NSApplication, NSImage
        info = NSBundle.mainBundle().localizedInfoDictionary() or NSBundle.mainBundle().infoDictionary()
        info['CFBundleName'] = APP_NAME
        if icon and os.path.exists(icon):
            NSApplication.sharedApplication().setApplicationIconImage_(NSImage.alloc().initWithContentsOfFile_(icon))
    except Exception:  # cosmetic only; the window still works
        pass


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=None)
    ap.add_argument('--icon', default=None)
    a = ap.parse_args()

    srv = server.make_server(a.root, 0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = 'http://127.0.0.1:%d/' % srv.server_address[1]

    dock_identity(a.icon)
    webview.settings['OPEN_EXTERNAL_LINKS_IN_BROWSER'] = True
    webview.settings['ALLOW_DOWNLOADS'] = False
    webview.create_window(APP_NAME, url, width=1280, height=880, min_size=(720, 500),
                          text_select=True)  # let text be selected and copied (Cmd+C)
    webview.start()
    srv.shutdown()
