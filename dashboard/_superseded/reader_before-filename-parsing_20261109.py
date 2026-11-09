"""Plan Dashboard reader. READ-ONLY on the project folders.
Reads plan.json plus the project files and returns one JSON-able dict.
Only writes its own 'last seen' copy in the app data folder."""
import csv, json, os, re, datetime as dt
from pathlib import Path

IMG_EXT = {'.png', '.jpg', '.jpeg', '.webp'}
STALE_DAYS = 7


def default_root():
    env = os.environ.get('PERSIAN_STORIES')
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent.parent / 'Persian Stories'


def app_data_dir():
    env = os.environ.get('PLAN_DASHBOARD_DATA')
    p = Path(env) if env else Path.home() / 'Library' / 'Application Support' / 'PlanDashboard'
    p.mkdir(parents=True, exist_ok=True)
    return p


def iso(ts):
    return dt.datetime.fromtimestamp(ts).astimezone().isoformat(timespec='seconds')


def mtime(p):
    try:
        return Path(p).stat().st_mtime
    except OSError:
        return None


def parse_iso(s):
    try:
        return dt.datetime.fromisoformat(s)
    except Exception:
        return None


def fmt(ts):
    return dt.datetime.fromtimestamp(ts).strftime('%b %d %I:%M %p').replace(' 0', ' ')


def list_films(root):
    return sorted(p.name for p in (root / 'Films').glob('EP*') if (p / 'plan.json').exists() or (p / 'film.yaml').exists())


def film_dir(root, film):
    films = list_films(root)
    if not films:
        raise FileNotFoundError('No Films/EP*/plan.json or film.yaml found under ' + str(root))
    if film in films:
        return root / 'Films' / film
    if film:
        for f in films:
            if f.startswith(film):
                return root / 'Films' / f
    return root / 'Films' / films[-1]


# ---------- simple readers ----------
def task_order(t):
    """Sort key: the task's "order" number in plan.json; tasks without one go last (in plan order)."""
    o = t.get('order')
    if isinstance(o, bool):
        o = None
    try:
        return (0, float(o))
    except (TypeError, ValueError):
        return (1, 0.0)


def planless_plan(fy):
    """Stand-in plan for a film that has film.yaml but no plan.json (for example a film published before plans existed).
    One line per gate from film.yaml; nothing is invented beyond what film.yaml says."""
    fg = fy.get('gates') if isinstance(fy.get('gates'), dict) else {}
    pd = fy.get('publish_date', '')
    pub = ''
    try:
        d = dt.date.fromisoformat(pd)
        pub = '%s %d' % (d.strftime('%b'), d.day)
    except (ValueError, TypeError):
        pass
    gates = []
    for i, (k, v) in enumerate(sorted(fg.items()), 1):
        closed = str(v).strip().lower() == 'closed'
        gates.append({'id': k, 'name': 'Gate %s: %s' % (k.lstrip('G'), 'closed' if closed else (str(v) or 'no state')),
                      'tasks': [{'id': k, 'n': 'Gate state from film.yaml: %s' % v, 'o': 'Both', 's': 'done' if closed else 'todo',
                                 'order': 1, 'out': '', 'evidence': '', 'file': 'film.yaml'}]})
    meta = {'version': 'no plan file', 'publish': pub, 'spend': '', 'updated': '', 'gate_state_from_film_yaml': dict(fg)}
    return {'meta': meta, 'gates': gates, 'standing': []}


def sorted_gates(gates):
    return [dict(g, tasks=sorted(g['tasks'], key=task_order)) for g in gates]


def strip_comment(v):
    """Drop a trailing '# comment' (a # at the start or after a space, outside quotes)."""
    quote = None
    for i, ch in enumerate(v):
        if quote:
            if ch == quote:
                quote = None
        elif ch in '"\'':
            quote = ch
        elif ch == '#' and (i == 0 or v[i - 1] in ' \t'):
            return v[:i]
    return v


def read_film_yaml(path):
    out = {}
    try:
        text = Path(path).read_text(encoding='utf-8')
    except OSError:
        return out
    for line in text.splitlines():
        m = re.match(r'^([A-Za-z_]+):\s*(.*)$', line)
        if not m:
            continue
        k, v = m.group(1), strip_comment(m.group(2)).strip()
        if v.startswith('{') and v.endswith('}'):
            parts, depth, cur = [], 0, ''
            for ch in v[1:-1]:
                if ch in '[{':
                    depth += 1
                if ch in ']}':
                    depth -= 1
                if ch == ',' and depth == 0:
                    parts.append(cur)
                    cur = ''
                else:
                    cur += ch
            parts.append(cur)
            d = {}
            for part in parts:
                if ':' in part:
                    a, b = part.split(':', 1)
                    d[a.strip()] = b.strip()
            out[k] = d
        else:
            out[k] = v
    return out


def num(x):
    try:
        return float(str(x).replace(',', '').replace('$', '').strip())
    except Exception:
        return None


def read_csv(path):
    try:
        with open(path, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except OSError:
        return []


def film_spend(root, ep_code):
    total, rows = 0.0, 0
    for r in read_csv(root / '05_ops' / 'cost-log.csv'):
        if (r.get('episode') or '').strip() == ep_code:
            v = num(r.get('cost_usd'))
            if v is not None:
                total += v
                rows += 1
    return round(total, 3), rows


def count_pictures(fd):
    n = 0
    for sub in ('02_cast', '03_world'):
        base = fd / sub
        if not base.exists():
            continue
        for p in base.rglob('*'):
            rel = p.relative_to(base).parts
            if len(rel) > 2 or any(x.startswith('_') for x in rel[:-1]):
                continue
            if p.is_file() and p.suffix.lower() in IMG_EXT:
                n += 1
    return n


# ---------- evidence check ----------
PATH_HINT = re.compile(r'/|\.(html|md|csv|json|mp3|m4a|png|jpg|yaml|srt|mp4|txt|wav)\b', re.I)
DIR_PREFIX = re.compile(r'((?:[\w.&\- ]+/)+)[^/]*$')


def _exists_any(piece, bases):
    words = piece.split(' ')
    for i in range(len(words)):
        cand = ' '.join(words[i:]).strip().rstrip('.')
        if not cand:
            continue
        for b in bases:
            if (b / cand).exists():
                return True
    return False


def check_evidence(task, bases):
    """Paths named in a done task's 'file' field that are not on disk."""
    text = task.get('file') or ''
    if not text:
        return None
    text = re.split(r'\s\(', text)[0]
    missing, last_dir = [], ''
    for piece in re.split(r',\s*|\s+and\s+', text):
        piece = piece.strip()
        if not piece or not PATH_HINT.search(piece):
            continue
        full = last_dir + piece if ('/' not in piece and last_dir) else piece
        ok = _exists_any(full, bases) or _exists_any(piece, bases)
        if not ok and ('/' in piece or re.search(r'\.\w{2,4}$', piece)):
            missing.append(piece)
        m = DIR_PREFIX.search(full)
        if m:
            last_dir = m.group(1).split('  ')[-1]
    return missing


# ---------- plan diff ----------
def _flat(plan, by_id):
    m = {}
    for g in plan['gates']:
        for t in g['tasks']:
            key = t['id'] if by_id else t['n'].strip().lower()
            m[key] = {'gate': g['id'], 'n': t['n'], 's': t.get('s'), 'due': t.get('due'),
                      'o': t.get('o'), 'id': t.get('id')}
    return m


def diff_plans(old, new):
    has_ids = lambda p: all('id' in t for g in p['gates'] for t in g['tasks'])
    by_id = has_ids(old) and has_ids(new)
    mo, mn = _flat(old, by_id), _flat(new, by_id)
    out = []
    for k, t in mn.items():
        if k not in mo:
            out.append({'kind': 'added', 'gate': t['gate'], 'task': t['n'],
                        'detail': ' · '.join(x for x in (t['id'], t['o'], 'due ' + str(t['due'])) if x)})
    for k, t in mo.items():
        if k not in mn:
            out.append({'kind': 'removed', 'gate': t['gate'], 'task': t['n'], 'detail': ''})
    for k, t in mn.items():
        o = mo.get(k)
        if not o:
            continue
        for f, label in (('s', 'status'), ('due', 'due date'), ('o', 'owner')):
            if (o.get(f) or '') != (t.get(f) or ''):
                out.append({'kind': label, 'gate': t['gate'], 'task': t['n'],
                            'detail': '%s → %s' % (o.get(f) or '—', t.get(f) or '—')})
        if by_id and o['n'] != t['n']:
            out.append({'kind': 'renamed', 'gate': t['gate'], 'task': t['n'], 'detail': 'was: ' + o['n']})
    return out


def newest_superseded_plan(fd):
    best, bv = None, -1
    for p in (fd / '_superseded').glob('plan_v*_*.json'):
        m = re.match(r'plan_v(\d+)_', p.name)
        if m and int(m.group(1)) > bv:
            best, bv = p, int(m.group(1))
    return best


# ---------- subscriptions ----------
def read_subscriptions(root, today):
    rows = read_csv(root / '00_admin' / 'subscriptions.csv')  # the current file; _vN copies are history
    bal = {r['vendor']: r for r in read_csv(root / '00_admin' / 'credit-balances.csv')}
    cards, now_total, later = [], 0.0, []
    for r in rows:
        price = num(r.get('price_usd_per_month')) or 0.0
        trial = (r.get('status_for_project') or '').lower().startswith('trial')
        nxt = r.get('next_charge_date') or ''
        unit = r.get('credits_unit') or ''
        total, used, left = num(r.get('credits_total')), num(r.get('credits_used')), num(r.get('credits_left'))
        b = bal.get(r['vendor'])
        if b:
            total = total if total is not None else num(b.get('total'))
            used = used if used is not None else num(b.get('used'))
            left = left if left is not None else num(b.get('left'))
            unit = unit or b.get('unit', '')
        if r.get('type') == 'subscription' and price:
            if trial:
                later.append((nxt, price))
            else:
                now_total += price
        age = None
        try:
            age = (today - dt.date.fromisoformat(r.get('as_of') or '')).days
        except Exception:
            pass
        cards.append({'vendor': r['vendor'], 'what': r.get('what_it_is'), 'plan': r.get('plan'),
                      'type': r.get('type'), 'price': price, 'trial': trial, 'next_charge': nxt,
                      'note': r.get('promo_or_note'), 'unit': unit, 'total': total, 'used': used,
                      'left': left, 'as_of': r.get('as_of'), 'age_days': age,
                      'stale': age is not None and age > STALE_DAYS,
                      'how_known': r.get('how_balance_known'), 'status': r.get('status_for_project')})
    cards.sort(key=lambda c: (c['next_charge'] == '', c['next_charge']))
    return {'cards': cards, 'monthly_now': round(now_total, 2),
            'monthly_later': round(now_total + sum(p for _, p in later), 2) if later else None,
            'later_date': max([d for d, _ in later if d], default=''),
            'source': '00_admin/subscriptions.csv'}


# ---------- main ----------
def build(root=None, film=None, now=None):
    root = Path(root) if root else default_root()
    now = now or dt.datetime.now().astimezone()
    fd = film_dir(root, film)
    plan_path = fd / 'plan.json'
    fy_path = fd / 'film.yaml'
    fy = read_film_yaml(fy_path)
    planless = not plan_path.exists()
    plan = planless_plan(fy) if planless else json.loads(plan_path.read_text(encoding='utf-8'))
    meta = plan['meta']
    ep_code = fd.name.split('_')[0]

    plan_saved = mtime(fy_path) if planless else mtime(plan_path)
    stamp = parse_iso(meta.get('updated', ''))
    watch = {'film.yaml': fy_path, 'cost-log.csv': root / '05_ops' / 'cost-log.csv',
             'subscriptions.csv': root / '00_admin' / 'subscriptions.csv',
             'credit-balances.csv': root / '00_admin' / 'credit-balances.csv'}
    files = {n: mtime(p) for n, p in watch.items() if mtime(p)}
    newest_name = max(files, key=files.get) if files else None
    older_than = [n for n in ('film.yaml', 'cost-log.csv') if files.get(n) and files[n] > plan_saved + 1]

    warnings = []
    mismatch = False
    if planless:
        older_than = []
        warnings.append({'level': 'info', 'title': 'No plan file for this film',
                         'detail': 'Films/%s has film.yaml but no plan.json (made before plans existed, or not started). Showing the gate states from film.yaml and the spend from cost-log.csv only.' % fd.name})
    if stamp:
        if stamp.timestamp() > now.timestamp() + 60:
            mismatch = True
            warnings.append({'level': 'warn', 'title': 'Plan stamp is in the future',
                             'detail': 'plan.json says it was updated %s, which is later than now. The stamp does not match the real time.' % meta.get('updated')})
        elif stamp.timestamp() > plan_saved + 120:
            mismatch = True
            warnings.append({'level': 'warn', 'title': 'Plan stamp does not match the save time',
                             'detail': 'plan.json says it was updated %s, but the file was saved at %s on the Mac.' % (fmt(stamp.timestamp()), fmt(plan_saved))})
    if older_than:
        warnings.append({'level': 'info', 'title': 'Plan is older than %d file%s' % (len(older_than), '' if len(older_than) == 1 else 's'),
                         'detail': 'Changed after plan.json was saved: ' + ', '.join(older_than) + '. The plan may not reflect them yet.'})

    pg = meta.get('gate_state_from_film_yaml') or {}
    fg = fy.get('gates') if isinstance(fy.get('gates'), dict) else {}
    diffs = ['%s: plan says %s, film.yaml says %s' % (k, pg.get(k), fg.get(k)) for k in sorted(set(pg) | set(fg)) if pg.get(k) != fg.get(k)]
    if diffs:
        warnings.append({'level': 'warn', 'title': 'Gate state differs from film.yaml', 'detail': '; '.join(diffs)})

    spent_yaml = num((fy.get('budget') or {}).get('spent_usd'))
    spent_log, nrows = film_spend(root, ep_code)
    if spent_yaml is not None and abs(spent_yaml - spent_log) > 0.005:
        warnings.append({'level': 'warn', 'title': 'Spend differs from cost-log.csv',
                         'detail': 'film.yaml says $%.2f; cost-log.csv has $%.2f for %s (%d rows).' % (spent_yaml, spent_log, ep_code, nrows)})

    pd = fy.get('publish_date', '')
    pm = re.search(r'([A-Z][a-z]{2}) (\d{1,2})', meta.get('publish', ''))
    if pd in ('', 'null', None):
        warnings.append({'level': 'warn', 'title': 'film.yaml has no publish date', 'detail': 'The plan says "%s".' % meta.get('publish')})
    elif pm:
        try:
            d = dt.date.fromisoformat(pd)
            if (d.strftime('%b'), d.day) != (pm.group(1), int(pm.group(2))):
                warnings.append({'level': 'warn', 'title': 'Publish date differs', 'detail': 'film.yaml says %s; the plan says "%s".' % (pd, meta.get('publish'))})
        except ValueError:
            pass

    pics = count_pictures(fd)
    acc = num((fy.get('image_brief') or {}).get('accepted'))
    if acc is not None and int(acc) != pics:
        warnings.append({'level': 'warn', 'title': 'Picture count differs',
                         'detail': 'film.yaml says %d accepted; %d image files are filed in 02_cast and 03_world.' % (acc, pics)})

    bases = [fd, root, root.parent]
    for g in ([] if planless else plan['gates']):
        for t in g['tasks']:
            if t.get('s') != 'done':
                continue
            tid = t.get('id', g['id'])
            if not t.get('evidence') and not t.get('file'):
                warnings.append({'level': 'info', 'title': 'Done task has no evidence', 'detail': '%s · %s' % (tid, t['n'])})
                continue
            miss = check_evidence(t, bases)
            if miss:
                warnings.append({'level': 'warn', 'title': 'Done task: file not found on disk',
                                 'detail': '%s · "%s" points to %s.' % (tid, t['n'], '; '.join(miss))})

    subs = read_subscriptions(root, now.date())
    stale = [c['vendor'] for c in subs['cards'] if c['stale'] and (c['total'] is not None or c['left'] is not None)]
    if stale:
        warnings.append({'level': 'info', 'title': 'Balance is old (over %d days)' % STALE_DAYS, 'detail': ', '.join(stale)})
    for c in subs['cards']:
        if c['trial'] and pd and pd != 'null' and c['next_charge'] and pd >= c['next_charge']:
            warnings.append({'level': 'warn', 'title': c['vendor'] + ' licence',
                             'detail': 'Publish date %s is on or after %s, when the paid plan starts. Make sure it is active.' % (pd, c['next_charge'])})

    data_dir = app_data_dir()
    seen_path = data_dir / ('last_seen_%s.json' % ep_code)
    if planless:
        since_seen = None
    elif seen_path.exists():
        try:
            seen = json.loads(seen_path.read_text(encoding='utf-8'))
            since_seen = {'from_version': seen['meta'].get('version'), 'to_version': meta.get('version'), 'items': diff_plans(seen, plan)}
        except Exception:
            since_seen = None
    else:
        seen_path.write_text(json.dumps(plan, ensure_ascii=False), encoding='utf-8')
        since_seen = {'from_version': meta.get('version'), 'to_version': meta.get('version'), 'items': [], 'first_run': True}
    prev = None if planless else newest_superseded_plan(fd)
    vs_prev = None
    if prev:
        try:
            old = json.loads(prev.read_text(encoding='utf-8'))
            vs_prev = {'from_version': old['meta'].get('version'), 'to_version': meta.get('version'), 'items': diff_plans(old, plan)}
        except Exception:
            pass

    return {
        'generated_at': now.isoformat(timespec='seconds'),
        'film': fd.name, 'films': list_films(root),
        'times': {'refreshed': now.isoformat(timespec='seconds'), 'plan_stamped': meta.get('updated'),
                  'plan_saved': iso(plan_saved), 'newest_file': iso(files[newest_name]) if newest_name else None,
                  'newest_file_name': newest_name, 'stamp_mismatch': mismatch},
        'plan': {'version': meta.get('version'), 'publish': meta.get('publish'), 'spend': meta.get('spend'),
                 'gates': sorted_gates(plan['gates']), 'standing': plan.get('standing', [])},
        'spend': {'total_usd': spent_log, 'rows': nrows, 'episode': ep_code,
                  'cost_log': str(root / '05_ops' / 'cost-log.csv')},
        'warnings': warnings,
        'changes': {'since_seen': since_seen, 'vs_previous': vs_prev},
        'subscriptions': subs,
    }


def mark_seen(root=None, film=None):
    root = Path(root) if root else default_root()
    fd = film_dir(root, film)
    if not (fd / 'plan.json').exists():
        return False   # nothing to mark for a film without a plan file
    plan = json.loads((fd / 'plan.json').read_text(encoding='utf-8'))
    (app_data_dir() / ('last_seen_%s.json' % fd.name.split('_')[0])).write_text(json.dumps(plan, ensure_ascii=False), encoding='utf-8')
    return True


if __name__ == '__main__':
    print(json.dumps(build(), indent=2, ensure_ascii=False))
