"""A film folder with film.yaml but no plan.json (EP01) must be listed and shown, without inventing a plan."""
import os, sys, tempfile, unittest, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import reader


class PlanlessFilm(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        os.environ['PLAN_DASHBOARD_DATA'] = str(self.root / 'appdata')
        (self.root / 'appdata').mkdir()
        (self.root / '05_ops').mkdir()
        (self.root / '00_admin').mkdir()
        old = self.root / 'Films' / 'EP01_zal'
        old.mkdir(parents=True)
        (old / 'film.yaml').write_text('film: EP01\nslug: zal\ngates: {G1: closed, G2: closed, G3: closed}\n'
                                       'publish_date: 2026-10-27\nbudget: {ceiling_usd: 100}\n', encoding='utf-8')
        new = self.root / 'Films' / 'EP02_x'
        new.mkdir()
        (new / 'film.yaml').write_text('film: EP02\n', encoding='utf-8')
        (new / 'plan.json').write_text(json.dumps({'meta': {'version': 'v1', 'updated': '', 'publish': 'Nov 10', 'spend': ''},
                                                   'gates': [], 'standing': []}), encoding='utf-8')

    def tearDown(self):
        self.tmp.cleanup()

    def test_both_films_are_listed(self):
        self.assertEqual(reader.list_films(self.root), ['EP01_zal', 'EP02_x'])

    def test_planless_film_builds_from_film_yaml(self):
        d = reader.build(root=self.root, film='EP01_zal')
        self.assertEqual(d['film'], 'EP01_zal')
        self.assertEqual([g['id'] for g in d['plan']['gates']], ['G1', 'G2', 'G3'])
        self.assertTrue(all(t['s'] == 'done' for g in d['plan']['gates'] for t in g['tasks']))
        self.assertEqual(d['plan']['publish'], 'Oct 27')
        self.assertTrue(any(w['title'] == 'No plan file for this film' for w in d['warnings']))
        self.assertFalse(any(w['level'] == 'warn' and 'Gate state differs' in w['title'] for w in d['warnings']))
        self.assertIsNone(d['changes']['since_seen'])

    def test_planless_film_does_not_write_a_seen_copy(self):
        reader.build(root=self.root, film='EP01_zal')
        self.assertEqual(list((self.root / 'appdata').iterdir()), [])
        self.assertFalse(reader.mark_seen(self.root, 'EP01_zal'))

    def test_film_with_a_plan_is_unchanged(self):
        d = reader.build(root=self.root, film='EP02_x')
        self.assertFalse(any(w['title'] == 'No plan file for this film' for w in d['warnings']))


if __name__ == '__main__':
    unittest.main()
