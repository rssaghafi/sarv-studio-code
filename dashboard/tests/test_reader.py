"""Tests for reader.py. Run:  python3 -m unittest discover -s tests -v
Uses a throw-away copy of the real data (never writes to the project)."""
import json, os, re, shutil, sys, tempfile, unittest, datetime as dt
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import reader  # noqa: E402

REAL = Path(os.environ.get('PERSIAN_STORIES', HERE.parent.parent.parent / 'Persian Stories'))
FILM = 'EP02_rostam-and-sohrab'


def make_fixture(tmp, plan=None, film_yaml=None):
    """Copy only the files the reader looks at; fake 21 pictures."""
    root = Path(tmp) / 'Persian Stories'
    fd = root / 'Films' / FILM
    (fd / '_superseded').mkdir(parents=True)
    shutil.copy2(REAL / 'Films' / FILM / 'plan.json', fd / 'plan.json')
    shutil.copy2(REAL / 'Films' / FILM / 'film.yaml', fd / 'film.yaml')
    for p in (REAL / 'Films' / FILM / '_superseded').glob('plan_v*.json'):
        shutil.copy2(p, fd / '_superseded' / p.name)
    (root / '05_ops').mkdir(); (root / '00_admin').mkdir()
    shutil.copy2(REAL / '05_ops' / 'cost-log.csv', root / '05_ops')
    for n in ('subscriptions.csv', 'credit-balances.csv'):
        shutil.copy2(REAL / '00_admin' / n, root / '00_admin')
    for i in range(29):
        d = fd / ('02_cast' if i < 13 else '03_world')
        d.mkdir(exist_ok=True)
        (d / ('pic%02d.png' % i)).write_bytes(b'x')
    if plan:
        shutil.copy2(plan, fd / 'plan.json')
    if film_yaml:
        shutil.copy2(film_yaml, fd / 'film.yaml')
    return root


class T(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ['PLAN_DASHBOARD_DATA'] = str(Path(self.tmp) / 'appdata')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def titles(self, d):
        return [w['title'] for w in d['warnings']]

    def test_clean_project_has_no_hard_warnings(self):
        root = make_fixture(self.tmp)
        # the live film.yaml can lag behind the cost log; make the copy agree so only reader errors show
        y = root / 'Films' / FILM / 'film.yaml'
        total = reader.film_spend(root, 'EP02')[0]
        y.write_text(re.sub(r'spent_usd: [0-9.]+', 'spent_usd: %s' % total, y.read_text()))
        # same for the plan stamp vs. its save time
        p = root / 'Films' / FILM / 'plan.json'
        stamp = reader.parse_iso(json.loads(p.read_text())['meta']['updated']).timestamp()
        os.utime(p, (stamp, stamp))
        # evidence files do not exist in the fixture, so ignore that one check
        d = reader.build(root, now=dt.datetime.now().astimezone())
        hard = [w for w in d['warnings'] if w['level'] == 'warn' and 'not found on disk' not in w['title']]
        self.assertEqual(hard, [], hard)

    def test_old_film_yaml_flags_the_known_drift(self):
        old = REAL / 'Films' / FILM / '_superseded' / 'film_v1_20261028.yaml'
        root = make_fixture(self.tmp, film_yaml=old)
        d = reader.build(root)
        t = self.titles(d)
        self.assertIn('Spend differs from cost-log.csv', t)
        self.assertIn('film.yaml has no publish date', t)
        self.assertIn('Picture count differs', t)

    def test_future_stamp_is_flagged(self):
        root = make_fixture(self.tmp)
        past = dt.datetime(2026, 10, 28, 12, 0).astimezone()
        d = reader.build(root, now=past)
        self.assertIn('Plan stamp is in the future', self.titles(d))
        self.assertTrue(d['times']['stamp_mismatch'])

    def test_stamp_later_than_save_is_flagged(self):
        root = make_fixture(self.tmp)
        p = root / 'Films' / FILM / 'plan.json'
        plan = json.loads(p.read_text())
        plan['meta']['updated'] = '2026-10-28T21:30-05:00'  # the real v6 mistake
        p.write_text(json.dumps(plan))
        os.utime(p, (dt.datetime(2026, 10, 28, 18, 19).timestamp(),) * 2)
        d = reader.build(root, now=dt.datetime(2026, 10, 29, 9, 0).astimezone())
        self.assertIn('Plan stamp does not match the save time', self.titles(d))

    def test_file_newer_than_plan_flagged(self):
        root = make_fixture(self.tmp)
        p = root / 'Films' / FILM / 'plan.json'
        os.utime(p, (1000000000,) * 2)
        d = reader.build(root)
        self.assertTrue(any(w['title'].startswith('Plan is older than') for w in d['warnings']))

    def test_gate_mismatch(self):
        root = make_fixture(self.tmp)
        y = root / 'Films' / FILM / 'film.yaml'
        plan_g3 = json.loads((root / 'Films' / FILM / 'plan.json').read_text())['meta']['gate_state_from_film_yaml']['G3']
        other = 'pending' if plan_g3 == 'closed' else 'closed'
        text = y.read_text()
        self.assertRegex(text, r'G3: \w+')
        y.write_text(re.sub(r'G3: \w+', 'G3: ' + other, text, count=1))
        self.assertIn('Gate state differs from film.yaml', self.titles(reader.build(root)))

    def test_evidence_missing_and_present(self):
        root = make_fixture(self.tmp)
        fd = root / 'Films' / FILM
        (fd / 'Output' / 'G1').mkdir(parents=True)
        (fd / 'Output' / 'G1' / 'real file v1.html').write_text('x')
        t_ok = {'file': 'Output/G1/real file v1.html (on your Mac)'}
        t_bad = {'file': 'Output/G1/missing.html (on your Mac)'}
        t_mix = {'file': 'Output/G1/real file v1.html, missing2.md'}
        bases = [fd, root, root.parent]
        self.assertEqual(reader.check_evidence(t_ok, bases), [])
        self.assertEqual(reader.check_evidence(t_bad, bases), ['Output/G1/missing.html'])
        self.assertEqual(reader.check_evidence(t_mix, bases), ['missing2.md'])
        self.assertEqual(reader.check_evidence({'file': 'film.yaml (G1 closed)'}, bases), [])

    def test_evidence_names_with_brackets_and_and(self):
        root = make_fixture(self.tmp)
        fd = root / 'Films' / FILM
        (fd / 'Output' / 'G4').mkdir(parents=True)
        (fd / 'Output' / 'G4' / 'picture review v3 (Opus).html').write_text('x')
        (fd / 'Output' / 'G4' / 'frames and animatic packet v3.html').write_text('x')
        (fd / 'Output' / 'G4' / 'dir_one').mkdir()
        (fd / 'Output' / 'G4' / 'dir_two').mkdir()
        bases = [fd, root, root.parent]
        self.assertEqual(reader.check_evidence({'file': 'Output/G4/picture review v3 (Opus).html'}, bases), [])
        self.assertEqual(reader.check_evidence({'file': 'Output/G4/frames and animatic packet v3.html'}, bases), [])
        self.assertEqual(reader.check_evidence({'file': 'Output/G4/dir_one/, Output/G4/dir_two/ (clips on your Mac)'}, bases), [])
        # a real list with one missing item is still reported
        self.assertEqual(reader.check_evidence({'file': 'Output/G4/frames and animatic packet v3.html, gone.md'}, bases), ['gone.md'])
        self.assertEqual(reader.check_evidence({'file': 'Output/G4/dir_one/ and Output/G4/nope/'}, bases), ['Output/G4/nope/'])

    def test_diff_added_removed_status_and_ids(self):
        mk = lambda tasks: {'gates': [{'id': 'G1', 'tasks': tasks}]}
        old = mk([{'id': 'G1-01', 'n': 'A', 's': 'todo', 'due': 'Oct 1', 'o': 'Claude'},
                  {'id': 'G1-02', 'n': 'B', 's': 'todo', 'due': 'Oct 2', 'o': 'Reza'}])
        new = mk([{'id': 'G1-01', 'n': 'A renamed', 's': 'done', 'due': 'Oct 1', 'o': 'Claude'},
                  {'id': 'G1-03', 'n': 'C', 's': 'todo', 'due': 'Oct 3', 'o': 'Reza'}])
        kinds = sorted((i['kind'], i['task']) for i in reader.diff_plans(old, new))
        self.assertIn(('added', 'C'), kinds)
        self.assertIn(('removed', 'B'), kinds)
        self.assertIn(('status', 'A renamed'), kinds)
        self.assertIn(('renamed', 'A renamed'), kinds)

    def test_diff_old_plan_without_ids_matches_by_name(self):
        v6 = json.loads((REAL / 'Films' / FILM / '_superseded' / 'plan_v6_20261028.json').read_text())
        v8 = json.loads((REAL / 'Films' / FILM / '_superseded' / 'plan_v8_20261028.json').read_text())
        self.assertEqual(reader.diff_plans(v6, v8), [])

    def test_changes_since_seen(self):
        root = make_fixture(self.tmp)
        d1 = reader.build(root)
        self.assertTrue(d1['changes']['since_seen'].get('first_run'))
        p = root / 'Films' / FILM / 'plan.json'
        plan = json.loads(p.read_text())
        plan['gates'][3]['tasks'].pop()      # remove a task
        next(t for g in plan['gates'] for t in g['tasks'] if t['s'] != 'done')['s'] = 'done'
        plan['gates'][3]['tasks'].append({'id': 'G3-99', 'n': 'New task', 'o': 'Claude', 'due': 'Nov 2', 's': 'todo', 'out': 'x'})
        p.write_text(json.dumps(plan))
        d2 = reader.build(root)
        kinds = [i['kind'] for i in d2['changes']['since_seen']['items']]
        self.assertIn('added', kinds); self.assertIn('removed', kinds); self.assertIn('status', kinds)
        reader.mark_seen(root)
        self.assertEqual(reader.build(root)['changes']['since_seen']['items'], [])

    def test_subscriptions_totals_and_current_file_only(self):
        root = make_fixture(self.tmp)
        # decoy older copy with a wrong price must be ignored
        (root / '00_admin' / 'subscriptions_v1_20261028.csv').write_text('vendor,price_usd_per_month\nElevenLabs,11.0\n')
        s = reader.build(root)['subscriptions']
        self.assertEqual(s['monthly_now'], 46.40)
        self.assertEqual(s['monthly_later'], 88.40)
        self.assertEqual(s['later_date'], '2026-11-18')
        names = [c['vendor'] for c in s['cards']]
        self.assertEqual(names[:4], ['OpenAI ChatGPT', 'ElevenLabs', 'Epidemic Sound', 'Claude (Anthropic)'])  # by next charge
        eleven = next(c for c in s['cards'] if c['vendor'] == 'ElevenLabs')
        self.assertEqual(eleven['price'], 6.40)
        self.assertEqual(next(c for c in s['cards'] if c['vendor'] == 'OpenAI ChatGPT')['plan'], 'Plus')

    def test_stale_balance_tag(self):
        root = make_fixture(self.tmp)
        s = reader.build(root, now=dt.datetime(2026, 11, 20, 9, 0).astimezone())['subscriptions']
        self.assertTrue(next(c for c in s['cards'] if c['vendor'] == 'fal')['stale'])

    def test_epidemic_licence_warning_when_publish_after_nov18(self):
        root = make_fixture(self.tmp)
        y = root / 'Films' / FILM / 'film.yaml'
        y.write_text(y.read_text().replace('publish_date: 2026-11-10', 'publish_date: 2026-11-24'))
        self.assertIn('Epidemic Sound licence', self.titles(reader.build(root)))

    def test_spend_total_is_cost_log_sum(self):
        root = make_fixture(self.tmp)
        log = root / '05_ops' / 'cost-log.csv'
        with log.open('a', encoding='utf-8') as f:
            f.write('2026-10-31,EP02,test,fal,x,1,1.25,added by test\n2026-10-31,EP03,test,fal,x,1,9,other film\n')
        before, n = reader.film_spend(root, 'EP02')
        d = reader.build(root)
        self.assertEqual(d['spend']['total_usd'], before)
        self.assertEqual(d['spend']['rows'], n)
        self.assertEqual(d['spend']['cost_log'], str(log))
        self.assertAlmostEqual(before - reader.film_spend(make_fixture(Path(self.tmp) / 'b'), 'EP02')[0], 1.25, places=3)

    def test_tasks_sorted_by_order_field(self):
        root = make_fixture(self.tmp)
        p = root / 'Films' / FILM / 'plan.json'
        plan = json.loads(p.read_text())
        plan['gates'][0]['tasks'] = [{'id': 'G1-01', 'n': 'no order'}, {'id': 'G1-02', 'n': 'ten', 'order': 10},
                                     {'id': 'G1-03', 'n': 'two', 'order': 2}, {'id': 'G1-04', 'n': 'bad', 'order': 'x'},
                                     {'id': 'G1-05', 'n': 'nine', 'order': 9}]
        p.write_text(json.dumps(plan))
        before = p.read_bytes()
        gates = reader.build(root)['plan']['gates']
        self.assertEqual([t['n'] for t in gates[0]['tasks']], ['two', 'nine', 'ten', 'no order', 'bad'])
        self.assertEqual(p.read_bytes(), before)   # view only: plan.json untouched
        for g in gates:
            nums = [reader.task_order(t) for t in g['tasks']]
            self.assertEqual(nums, sorted(nums), g['id'])

    def test_read_only(self):
        root = make_fixture(self.tmp)
        before = {p: p.stat().st_mtime for p in root.rglob('*') if p.is_file()}
        reader.build(root)
        after = {p: p.stat().st_mtime for p in root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
