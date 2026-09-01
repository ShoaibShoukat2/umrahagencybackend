"""
Duplicate Package Check Script
================================
Run from the backend folder:
    python check_duplicates.py

Checks duplicates by:
  1. Same slug
  2. Same name
  3. Same travel_date + return_date combination
  4. Same name + travel_date (most reliable)
"""

import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from api.models import Package, RoomSharingPrice
from collections import defaultdict

def red(t):    return f'\033[91m{t}\033[0m'
def green(t):  return f'\033[92m{t}\033[0m'
def yellow(t): return f'\033[93m{t}\033[0m'
def cyan(t):   return f'\033[96m{t}\033[0m'
def bold(t):   return f'\033[1m{t}\033[0m'

SEP  = '─' * 70
SEP2 = '═' * 70

all_packages = list(Package.objects.all().order_by('id'))

print()
print(bold(SEP2))
print(bold('  DUPLICATE PACKAGE CHECK'))
print(bold(SEP2))
print(f'\n  Total packages in DB: {bold(str(len(all_packages)))}')

found_any = False

# ── 1. Duplicate slugs ────────────────────────────────────────────────────────
print(f'\n{cyan(bold("1. DUPLICATE SLUGS"))}')
print(SEP)

slug_map = defaultdict(list)
for p in all_packages:
    slug_map[p.slug].append(p)

dup_slugs = {k: v for k, v in slug_map.items() if len(v) > 1}
if not dup_slugs:
    print(f'  {green("✓ No duplicate slugs found.")}')
else:
    found_any = True
    print(f'  {red(f"⚠  {len(dup_slugs)} duplicate slug(s) found:")}')
    for slug, pkgs in dup_slugs.items():
        print(f'\n  Slug: {red(slug)}')
        for p in pkgs:
            prices = RoomSharingPrice.objects.filter(package=p)
            price_str = ', '.join(f'{pr.sharing_type}=S${pr.price}' for pr in prices) or 'NO PRICES'
            print(f'    [{p.id}] active={p.is_active}  travel={p.travel_date}  name={p.name}')
            print(f'         prices: {price_str}')

# ── 2. Duplicate names ────────────────────────────────────────────────────────
print(f'\n{cyan(bold("2. DUPLICATE NAMES"))}')
print(SEP)

name_map = defaultdict(list)
for p in all_packages:
    name_map[p.name.strip()].append(p)

dup_names = {k: v for k, v in name_map.items() if len(v) > 1}
if not dup_names:
    print(f'  {green("✓ No duplicate names found.")}')
else:
    found_any = True
    print(f'  {red(f"⚠  {len(dup_names)} duplicate name(s) found:")}')
    for name, pkgs in dup_names.items():
        print(f'\n  Name: {red(name)}')
        for p in pkgs:
            print(f'    [{p.id}] slug={p.slug}  active={p.is_active}  travel={p.travel_date}')

# ── 3. Duplicate travel_date + return_date ────────────────────────────────────
print(f'\n{cyan(bold("3. DUPLICATE TRAVEL DATE + RETURN DATE"))}')
print(SEP)

date_map = defaultdict(list)
for p in all_packages:
    key = f'{p.travel_date}|{p.return_date}'
    date_map[key].append(p)

dup_dates = {k: v for k, v in date_map.items() if len(v) > 1}
if not dup_dates:
    print(f'  {green("✓ No packages share the same travel + return dates.")}')
else:
    print(f'  {yellow(f"ℹ  {len(dup_dates)} date combination(s) shared by multiple packages:")}')
    for key, pkgs in dup_dates.items():
        travel, ret = key.split('|')
        print(f'\n  {travel} → {ret}')
        for p in pkgs:
            print(f'    [{p.id}] {p.name}  (slug: {p.slug})  active={p.is_active}')

# ── 4. Duplicate name + travel_date (strongest signal) ───────────────────────
print(f'\n{cyan(bold("4. DUPLICATE NAME + TRAVEL DATE  (strongest duplicate signal)"))}')
print(SEP)

name_date_map = defaultdict(list)
for p in all_packages:
    key = f'{p.name.strip().lower()}|{p.travel_date}'
    name_date_map[key].append(p)

dup_name_date = {k: v for k, v in name_date_map.items() if len(v) > 1}
if not dup_name_date:
    print(f'  {green("✓ No packages share the same name + travel date.")}')
else:
    found_any = True
    print(f'  {red(f"⚠  {len(dup_name_date)} exact duplicate(s) found (same name + travel date):")}')
    for key, pkgs in dup_name_date.items():
        name, date = key.split('|', 1)
        print(f'\n  Name: {red(name)}  |  Travel: {date}')
        for p in pkgs:
            print(f'    [{p.id}] slug={p.slug}  active={p.is_active}')

# ── 5. Full clean list ────────────────────────────────────────────────────────
print(f'\n{cyan(bold("5. ALL PACKAGES — CLEAN LIST"))}')
print(SEP)
print(f'  {"ID":<5} {"Active":<8} {"Travel Date":<14} {"Name"}')
print(f'  {"-"*5} {"-"*8} {"-"*14} {"-"*45}')
for p in sorted(all_packages, key=lambda x: x.travel_date):
    active_str = green('Yes') if p.is_active else red('No ')
    print(f'  {p.id:<5} {active_str:<8} {str(p.travel_date):<14} {p.name[:55]}')

# ── Summary ───────────────────────────────────────────────────────────────────
print()
print(bold(SEP2))
print(bold('  SUMMARY'))
print(bold(SEP2))
if not found_any:
    print(green(f'  ✓ No duplicates found! All {len(all_packages)} packages are unique.'))
else:
    if dup_slugs:
        print(red(  f'  ✗ {len(dup_slugs)} duplicate slug(s)'))
    if dup_names:
        print(red(  f'  ✗ {len(dup_names)} duplicate name(s)'))
    if dup_name_date:
        print(red(  f'  ✗ {len(dup_name_date)} exact duplicate(s) by name+date'))
    print()
    print(yellow('  To remove duplicates, run:'))
    print(yellow('      python fix_packages.py'))
print()
