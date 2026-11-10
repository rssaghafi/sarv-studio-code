"""Tests for server.py --lan rules. Run:  python3 -m unittest discover -s tests -v
Uses the same throw-away project copy as test_reader.py."""
import json, os, shutil, sys, tempfile, threading, unittest
from pathlib import Path
from unittest import mock
from urllib.error import HTTPError
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import server  # noqa: E402
from test_reader import make_fixture  # noqa: E402


class T(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.appdata = Path(self.tmp) / 'appdata'
        os.environ['PLAN_DASHBOARD_DATA'] = str(self.appdata)
        self._old_user = os.environ.get('SARV_USER')
        os.environ['SARV_USER'] = 'reza'
        self.addCleanup(lambda: os.environ.pop('SARV_USER', None) if self._old_user is None else os.environ.__setitem__('SARV_USER', self._old_user))
        self.root = make_fixture(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def serve(self, lan):
        srv = server.make_server(self.root, 0, lan)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.server_close)
        self.addCleanup(srv.shutdown)
        return srv

    def post_seen(self, srv):
        req = Request('http://127.0.0.1:%d/api/seen' % srv.server_address[1], data=b'', method='POST')
        try:
            with urlopen(req) as r:
                return r.status, json.loads(r.read())
        except HTTPError as e:
            return e.code, json.loads(e.read())

    def test_from_this_mac_rule(self):
        self.assertTrue(server.from_this_mac('127.0.0.1', '127.0.0.1'))
        self.assertTrue(server.from_this_mac('::1', '::1'))
        self.assertTrue(server.from_this_mac('192.168.1.5', '192.168.1.5'))   # Mac opening hostname.local
        self.assertFalse(server.from_this_mac('192.168.1.20', '192.168.1.5'))  # phone on the same Wi-Fi

    def test_lan_post_from_this_mac_allowed(self):
        srv = self.serve(lan=True)
        self.assertEqual(srv.server_address[0], '0.0.0.0')
        code, body = self.post_seen(srv)
        self.assertEqual(code, 200, body)
        self.assertTrue(any(self.appdata.iterdir()))

    def test_lan_post_from_other_device_rejected(self):
        srv = self.serve(lan=True)
        before = {p: p.stat().st_mtime for p in self.root.rglob('*') if p.is_file()}
        with mock.patch.object(server, 'from_this_mac', return_value=False):
            code, body = self.post_seen(srv)
        self.assertEqual(code, 403)
        self.assertIn('Read-only', body['error'])
        self.assertFalse(self.appdata.exists() and any(self.appdata.iterdir()))
        after = {p: p.stat().st_mtime for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def post(self, srv, path):
        req = Request('http://127.0.0.1:%d%s' % (srv.server_address[1], path), data=b'', method='POST')
        try:
            with urlopen(req) as r:
                return r.status, json.loads(r.read())
        except HTTPError as e:
            return e.code, json.loads(e.read())

    def test_cost_log_text_view(self):
        srv = self.serve(lan=True)
        with urlopen('http://127.0.0.1:%d/cost-log.csv' % srv.server_address[1]) as r:
            self.assertTrue(r.headers['Content-Type'].startswith('text/plain'))
            self.assertEqual(r.read(), (self.root / '05_ops' / 'cost-log.csv').read_bytes())

    def test_cost_log_view_of_another_person_and_bad_names(self):
        (self.root / '05_ops' / 'cost-log_edris.csv').write_text('date,episode\n2026-11-12,EP04\n', encoding='utf-8')
        srv = self.serve(lan=True)
        base = 'http://127.0.0.1:%d/cost-log.csv' % srv.server_address[1]
        with urlopen(base + '?person=edris') as r:
            self.assertEqual(r.read(), b'date,episode\n2026-11-12,EP04\n')
        with urlopen(base + '?person=..%2F..%2Fsecret') as r:  # not a name: falls back to this Mac's own log
            self.assertEqual(r.read(), (self.root / '05_ops' / 'cost-log.csv').read_bytes())

    def test_open_cost_log_only_from_this_mac(self):
        srv = self.serve(lan=True)
        ok = mock.Mock(returncode=0, stderr='')
        with mock.patch.object(server.subprocess, 'run', return_value=ok) as run:
            with mock.patch.object(server, 'from_this_mac', return_value=False):
                code, _ = self.post(srv, '/api/open-cost-log')
            self.assertEqual(code, 403)
            run.assert_not_called()
            code, body = self.post(srv, '/api/open-cost-log')
        self.assertEqual(code, 200, body)
        run.assert_called_once()
        self.assertEqual(run.call_args[0][0], ['open', str(self.root / '05_ops' / 'cost-log.csv')])

    def test_default_is_this_mac_only(self):
        srv = self.serve(lan=False)
        self.assertEqual(srv.server_address[0], '127.0.0.1')
        with mock.patch.object(server, 'from_this_mac', return_value=False):
            code, _ = self.post_seen(srv)   # rule not applied; only reachable from this Mac anyway
        self.assertEqual(code, 200)


if __name__ == '__main__':
    unittest.main()
