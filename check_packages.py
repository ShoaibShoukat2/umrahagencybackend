"""
Check script — compares packages in the local database vs
the packages currently shown on the live site API.

Run from the backend folder:
    python check_packages.py

What it checks:
  1. Local DB  — all packages (active + inactive)
  2. Live site — packages from https://backend.tmfouzy.sg/api/packages/
  3. Featured  — packages from /api/packages/featured/
  4. Mismatches: in DB but not on site, on site but not in DB
  5. is_active=False packages (hidden from site)
  6. Missing room prices
  7. Missing / blank fields that break display
"""

import os, sys, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from api.models import Package, RoomSharingPrice
from decimal import Decimal

try:
    import urllib.request
    import urllib.error
except ImportError:
    pass

LIVE_API      = 'https://backend.tmfouzy.sg/api/packages/?limit=200'
FEATURED_API  = 'https://backend.tmfouzy.sg/api/packages/featured/'

SEP  = '─' * 70
SEP2 = '═' * 70

# ─── colour helpers (works in most terminals) ─────────────────────────────────
def red(t):    return f'\033[91m{t}\033[0m'
def green(t):  return f'\033[92m{t}\033[0m'
def yellow(t): return f'\033[93m{t}\033[0m'
def cyan(t):   return f'\033[96m{t}\033[0m'
def bold(t):   return f'\033[1m{t}\033[0m'

# ─── fetch live data ──────────────────────────────────────────────────────────
def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'check-script/1.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(red(f'  HTTP {e.code} from {url}'))
        return None
    except Exception as e:
        print(red(f'  Could not reach {url}: {e}'))
        return None

# ─── local DB ─────────────────────────────────────────────────────────────────
db_all      = list(Package.objects.all().order_by('travel_date'))
db_active   = [p for p in db_all if p.is_active]
db_inactive = [p for p in db_all if not p.is_active]
db_featured = [p for p in db_active if p.is_featured]

db_slugs_active = {p.slug for p in db_active}
db_slugs_all    = {p.slug for p in db_all}

print()
print(bold(SEP2))
print(bold('  PACKAGE SYNC CHECK'))
print(bold(SEP2))

# ─── 1. DB summary ────────────────────────────────────────────────────────────
print(f'\n{cyan(bold("1. LOCAL DATABASE"))}')
print(SEP)
print(f'  Total packages  : {bold(str(len(db_all)))}')
print(f'  Active (visible): {green(str(len(db_active)))}')
print(f'  Inactive/hidden : {yellow(str(len(db_inactive)))}')
print(f'  Featured        : {green(str(len(db_featured)))}')

if db_inactive:
    print(f'\n  {yellow("Inactive packages (NOT shown on site):")}')
    for p in db_inactive:
        print(f'    {yellow("●")} [{p.id}] {p.name}  (slug: {p.slug})')

# ─── 2. Live site ─────────────────────────────────────────────────────────────
print(f'\n{cyan(bold("2. LIVE SITE  →  " + LIVE_API))}')
print(SEP)

live_data = fetch_json(LIVE_API)
if live_data is None:
    live_pkgs = []
    print(red('  Could not fetch live packages — skipping site comparison.'))
else:
    live_pkgs = live_data if isinstance(live_data, list) else live_data.get('results', [])
    print(f'  Packages returned by live API: {bold(str(len(live_pkgs)))}')

live_slugs = {p['slug'] for p in live_pkgs}

# Featured
feat_data = fetch_json(FEATURED_API)
feat_pkgs = []
if feat_data is not None:
    feat_pkgs = feat_data if isinstance(feat_data, list) else feat_data.get('results', [])
    print(f'  Featured packages on live API : {bold(str(len(feat_pkgs)))}')

# ─── 3. Mismatch: in DB (active) but NOT on live site ────────────────────────
print(f'\n{cyan(bold("3. IN LOCAL DB (active) but MISSING from live site"))}')
print(SEP)
missing_on_site = db_slugs_active - live_slugs
if not missing_on_site:
    print(f'  {green("✓ None — all active local packages are on the live site.")}')
else:
    print(f'  {red(f"⚠  {len(missing_on_site)} package(s) are active locally but NOT on the live site:")}')
    for p in db_active:
        if p.slug in missing_on_site:
            prices = RoomSharingPrice.objects.filter(package=p)
            price_str = ', '.join(
                f'{pr.sharing_type}=S${pr.price}' for pr in prices
            ) or red('NO PRICES')
            print(f'    {red("✗")} [{p.id}] {p.name}')
            print(f'         slug        : {p.slug}')
            print(f'         travel_date : {p.travel_date}')
            print(f'         prices      : {price_str}')

# ─── 4. On live site but NOT in local DB ─────────────────────────────────────
print(f'\n{cyan(bold("4. ON LIVE SITE but NOT in local DB"))}')
print(SEP)
extra_on_site = live_slugs - db_slugs_all
if not extra_on_site:
    print(f'  {green("✓ None — all live site packages exist in local DB.")}')
else:
    print(f'  {yellow(f"⚠  {len(extra_on_site)} package(s) on the live site are NOT in local DB:")}')
    for p in live_pkgs:
        if p['slug'] in extra_on_site:
            print(f'    {yellow("●")} {p.get("name","?")}  (slug: {p["slug"]})')

# ─── 5. Missing room prices ───────────────────────────────────────────────────
print(f'\n{cyan(bold("5. ACTIVE PACKAGES WITH NO ROOM PRICES"))}')
print(SEP)
no_prices = []
for p in db_active:
    if not RoomSharingPrice.objects.filter(package=p).exists():
        no_prices.append(p)
if not no_prices:
    print(f'  {green("✓ All active packages have at least one room price.")}')
else:
    print(f'  {red(f"⚠  {len(no_prices)} package(s) have NO prices set:")}')
    for p in no_prices:
        print(f'    {red("✗")} [{p.id}] {p.name}')

# ─── 6. Blank/missing critical fields ────────────────────────────────────────
print(f'\n{cyan(bold("6. ACTIVE PACKAGES WITH BLANK CRITICAL FIELDS"))}')
print(SEP)
field_issues = []
for p in db_active:
    issues = []
    if not p.short_description:
        issues.append('short_description empty')
    if not p.inclusions:
        issues.append('inclusions empty')
    if not p.hotel_name:
        issues.append('hotel_name empty')
    if p.max_capacity < 1:
        issues.append(f'max_capacity={p.max_capacity}')
    if issues:
        field_issues.append((p, issues))

if not field_issues:
    print(f'  {green("✓ All active packages have the key fields filled in.")}')
else:
    print(f'  {yellow(f"⚠  {len(field_issues)} package(s) have blank fields:")}')
    for p, issues in field_issues:
        print(f'    {yellow("●")} [{p.id}] {p.name}')
        for iss in issues:
            print(f'         {red("·")} {iss}')

# ─── 7. Full side-by-side list ────────────────────────────────────────────────
print(f'\n{cyan(bold("7. FULL LOCAL DB  vs  LIVE SITE  (active only)"))}')
print(SEP)
print(f'  {"ID":<5} {"Slug":<45} {"DB":^6} {"Site":^6} {"Featured":^9}')
print(f'  {"-"*5} {"-"*45} {"-"*6} {"-"*6} {"-"*9}')

for p in sorted(db_active, key=lambda x: x.travel_date):
    on_site  = green('  ✓  ') if p.slug in live_slugs  else red('  ✗  ')
    featured = green('  ✓  ') if p.is_featured else '   -  '
    slug_col = p.slug[:44]
    print(f'  {p.id:<5} {slug_col:<45} {green("  ✓  "):^6} {on_site:^6} {featured:^9}')

# ─── summary ──────────────────────────────────────────────────────────────────
print()
print(bold(SEP2))
print(bold('  SUMMARY'))
print(bold(SEP2))
total_issues = len(missing_on_site) + len(extra_on_site) + len(no_prices) + len(field_issues) + len(db_inactive)
if total_issues == 0:
    print(green(f'  ✓ Everything looks good! {len(db_active)} packages in sync.'))
else:
    if missing_on_site:
        print(red(  f'  ✗ {len(missing_on_site):>3} active local package(s) not on live site'))
    if extra_on_site:
        print(yellow(f'  ● {len(extra_on_site):>3} live site package(s) not in local DB'))
    if no_prices:
        print(red(  f'  ✗ {len(no_prices):>3} active package(s) have no room prices'))
    if field_issues:
        print(yellow(f'  ● {len(field_issues):>3} active package(s) have blank critical fields'))
    if db_inactive:
        print(yellow(f'  ● {len(db_inactive):>3} package(s) are inactive (hidden from site)'))
print()
