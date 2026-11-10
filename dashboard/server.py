"""Plan Dashboard local server. Read-only on the project folders.
Run:  python3 server.py [--open] [--port 8765] [--root "/path/to/Persian Stories"] [--lan]
--lan listens on all network addresses (other devices on the same Wi-Fi can view the page);
      "Mark as seen" is then accepted only from this Mac. Default: this Mac only (127.0.0.1).
Serves index.html and two small endpoints:
  GET  /api/data?film=EP02   -> everything the page shows
  POST /api/seen?film=EP02   -> "Mark as seen" (writes only the app's own last-seen copy)
  GET  /cost-log.csv         -> 05_ops/cost-log.csv as plain text (read-only view)
  POST /api/open-cost-log    -> opens cost-log.csv in the Mac's default app for .csv (this Mac only)
"""
import argparse, json, os, re, socket, subprocess, sys, threading, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reader  # noqa: E402

ROOT = None
LAN = False


def from_this_mac(client_ip, server_ip):
    """True for loopback, or when the sender's address is the address it reached us on
    (only this Mac can open a TCP connection from its own address to itself)."""
    if client_ip.startswith('127.') or client_ip in ('::1', '::ffff:127.0.0.1'):
        return True
    return client_ip == server_ip


def cost_log_path(person=None):
    """This Mac's own cost log (SARV_USER), or the named person's with ?person=<name>."""
    return reader.cost_log_for(Path(ROOT) if ROOT else reader.default_root(), person)


def mac_name():
    """This Mac's Bonjour name, e.g. Rezas-MacBook-Pro.local"""
    try:
        n = subprocess.run(['scutil', '--get', 'LocalHostName'], capture_output=True, text=True, timeout=2).stdout.strip()
    except Exception:
        n = ''
    n = n or socket.gethostname()
    return n if n.endswith('.local') else n + '.local'


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype='application/json; charset=utf-8'):
        if isinstance(body, str):
            body = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path in ('/', '/index.html'):
            return self._send(200, (HERE / 'index.html').read_text(encoding='utf-8'), 'text/html; charset=utf-8')
        if u.path == '/api/data':
            try:
                data = reader.build(ROOT, (q.get('film') or [None])[0])
                return self._send(200, json.dumps(data, ensure_ascii=False))
            except Exception as e:  # show a plain message in the page
                return self._send(500, json.dumps({'error': str(e)}))
        if u.path == '/cost-log.csv':
            try:
                return self._send(200, cost_log_path((q.get('person') or [None])[0]).read_bytes(), 'text/plain; charset=utf-8')
            except OSError as e:
                return self._send(404, 'cost-log.csv not found: %s' % e, 'text/plain')
        self._send(404, 'Not found', 'text/plain')

    def _from_this_mac(self):
        return from_this_mac(self.client_address[0], self.connection.getsockname()[0])

    def do_POST(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path == '/api/seen':
            if LAN and not self._from_this_mac():
                return self._send(403, json.dumps({'error': 'Read-only from other devices. Mark as seen on the Mac itself.'}))
            try:
                reader.mark_seen(ROOT, (q.get('film') or [None])[0])
                return self._send(200, json.dumps({'ok': True}))
            except Exception as e:
                return self._send(500, json.dumps({'error': str(e)}))
        if u.path == '/api/open-cost-log':
            if not self._from_this_mac():
                return self._send(403, json.dumps({'error': 'Only on the Mac itself.'}))
            f = cost_log_path((q.get('person') or [None])[0])
            if not f.is_file():
                return self._send(404, json.dumps({'error': 'cost-log.csv not found'}))
            r = subprocess.run(['open', str(f)], capture_output=True, text=True, timeout=10)
            return self._send(200 if r.returncode == 0 else 500, json.dumps({'ok': r.returncode == 0, 'error': r.stderr.strip() or None}))
        self._send(404, 'Not found', 'text/plain')


def make_server(root=None, port=0, lan=False):
    global ROOT, LAN
    ROOT, LAN = root, lan
    return ThreadingHTTPServer(('0.0.0.0' if lan else '127.0.0.1', port), Handler)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--root', default=None)
    ap.add_argument('--open', action='store_true')
    ap.add_argument('--lan', action='store_true', help='also serve to other devices on this network (read-only for them)')
    a = ap.parse_args()
    srv = make_server(a.root, a.port, a.lan)
    url = 'http://127.0.0.1:%d/' % srv.server_address[1]
    print('Plan Dashboard running at', url, '(Ctrl+C to stop)')
    if a.lan:
        print('On other devices: http://%s:%d/' % (mac_name(), srv.server_address[1]))
        print('WARNING: anyone on the same Wi-Fi can see this page (plan, costs, subscriptions).')
        print('         Other devices can only read; "Mark as seen" works only on this Mac.')
    if a.open:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
