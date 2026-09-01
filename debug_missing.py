"""
Debug script — figures out exactly WHY the 11 packages are not showing
on the live API despite being active in the DB.

Run:  python debug_missing.py
"""

import os, sys, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from api.models import Package
from django.utils import timezone
from datetime import date
import urllib.request

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'debug/1.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f'  ERROR fetching {url}: {e}')
        return None

def bold(t): return f'\033[1m{t}\033[0m'
def red(t):  return f'\033[91m{t}\033[0m'
def green(t):return f'\033[92m{t}\033[0m'
def yellow(t):return f'\033[93m{t}\033[0m'
def cyan(t): return f'\033[96m{t}\033[0m'

BASE = 'https://backend.tmfouzy.sg/api'

MISSING_IDS = [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 16]

print()
print(bold('=' * 70))
print(bold('  DEBUG: WHY ARE 11 PACKAGES MISSING FROM LIVE SITE?'))
print(bold('=' * 70))

today = date.today()
print(f'\n  Today (server): {today}')

# ── Check 1: DB state of missing packages ─────────────────────────────────────
print(f'\n{cyan(bold("CHECK 1 — DB state of the 11 missing packages"))}')
print('─' * 70)
pkgs = Package.objects.filter(id__in=MISSING_IDS).order_by('travel_date')
for p in pkgs:
    days_until = (p.travel_date - today).days
    prices = p.room_prices.all()
    price_str = ', '.join(f'{pr.sharing_type}=S${pr.price}' for pr in prices) or red('NO PRICES')
    past_flag = yellow(' ← PAST DATE') if days_until < 0 else green(f' ({days_until} days away)')
    print(f'  [{p.id}] {p.name}')
    print(f'       is_active={p.is_active}  travel_date={p.travel_date}{past_flag}')
    print(f'       category={p.category.slug}  is_featured={p.is_featured}')
    print(f'       prices: {price_str}')

# ── Check 2: Try fetching each slug directly from live API ────────────────────
print(f'\n{cyan(bold("CHECK 2 — Fetch each missing package by slug from live API"))}')
print('─' * 70)
for p in pkgs:
    url = f'{BASE}/packages/{p.slug}/'
    data = fetch(url)
    if data and 'id' in data:
        print(green(f'  ✓ [{p.id}] {p.slug} — FOUND on live API'))
    elif data and 'detail' in data:
        print(red(f'  ✗ [{p.id}] {p.slug} — {data["detail"]}'))
    else:
        print(red(f'  ✗ [{p.id}] {p.slug} — not found / error'))

# ── Check 3: Live API with different filters ──────────────────────────────────
print(f'\n{cyan(bold("CHECK 3 — Live API pagination & filter tests"))}')
print('─' * 70)

tests = [
    ('No limit param',         f'{BASE}/packages/'),
    ('limit=200',              f'{BASE}/packages/?limit=200'),
    ('limit=100',              f'{BASE}/packages/?limit=100'),
    ('category=umrah-packages',f'{BASE}/packages/?category__slug=umrah-packages&limit=200'),
    ('Sep packages by month',  f'{BASE}/packages/?month=9&year=2026'),
    ('Oct packages by month',  f'{BASE}/packages/?month=10&year=2026'),
    ('Nov packages by month',  f'{BASE}/packages/?month=11&year=2026'),
    ('Dec packages by month',  f'{BASE}/packages/?month=12&year=2026'),
]

for label, url in tests:
    data = fetch(url)
    if data is None:
        continue
    items = data if isinstance(data, list) else data.get('results', [])
    count = data.get('count', len(items)) if isinstance(data, dict) else len(items)
    print(f'  {label:<40} → {bold(str(len(items)))} returned  (total count={count})')

# ── Check 4: Serializer — does it have any computed filter? ───────────────────
print(f'\n{cyan(bold("CHECK 4 — Direct DB query mimicking API filter"))}')
print('─' * 70)
active_all = Package.objects.filter(is_active=True).order_by('travel_date')
print(f'  is_active=True in DB: {bold(str(active_all.count()))}')

future_only = active_all.filter(travel_date__gte=today)
print(f'  travel_date >= today ({today}): {bold(str(future_only.count()))}')

past_only = active_all.filter(travel_date__lt=today)
if past_only.exists():
    print(yellow(f'  travel_date < today (past packages): {past_only.count()}'))
    for p in past_only:
        print(yellow(f'    ● [{p.id}] {p.name}  travel_date={p.travel_date}'))

print()
print(bold('=' * 70))
print(bold('  DEBUG COMPLETE'))
print(bold('=' * 70))
print()
