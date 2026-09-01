"""
Fix script — cleans up duplicate packages and ensures all 2026 packages
are visible on the live site.

Run from the backend folder:
    python fix_packages.py

What it does:
  1. Finds all duplicate packages (same name, keeps the OLDER/original one)
  2. Deletes the duplicate copies (slug ending in -1, -2, etc.)
  3. Ensures all original packages have is_active=True
  4. Re-checks the live API to confirm they now appear

DRY RUN by default — set DRY_RUN = False to actually apply changes.
"""

import os, sys, django, json, re
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from api.models import Package, RoomSharingPrice, Booking

# ── Config ────────────────────────────────────────────────────────────────────
DRY_RUN = False   # Change to False to apply changes
# ─────────────────────────────────────────────────────────────────────────────

def red(t):    return f'\033[91m{t}\033[0m'
def green(t):  return f'\033[92m{t}\033[0m'
def yellow(t): return f'\033[93m{t}\033[0m'
def cyan(t):   return f'\033[96m{t}\033[0m'
def bold(t):   return f'\033[1m{t}\033[0m'

SEP = '─' * 70

try:
    import urllib.request
    def fetch_live_slugs():
        url = 'https://backend.tmfouzy.sg/api/packages/?limit=200'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'fix-script/1.0'})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read().decode())
                pkgs = data if isinstance(data, list) else data.get('results', [])
                return {p['slug'] for p in pkgs}
        except Exception as e:
            print(yellow(f'  Could not fetch live site: {e}'))
            return set()
except ImportError:
    def fetch_live_slugs(): return set()

print()
print(bold('=' * 70))
print(bold('  PACKAGE FIX SCRIPT' + (' [DRY RUN]' if DRY_RUN else ' [LIVE]')))
print(bold('=' * 70))

# ── Step 1: Find duplicates ───────────────────────────────────────────────────
print(f'\n{cyan(bold("STEP 1 — Find duplicate packages"))}')
print(SEP)

# A duplicate slug looks like: original-slug-1, original-slug-2, etc.
dup_pattern = re.compile(r'^(.+)-(\d+)$')

all_packages  = list(Package.objects.all().order_by('id'))
all_slugs     = {p.slug for p in all_packages}

to_delete   = []   # Package objects to remove
to_keep     = []   # Original packages to ensure active

for pkg in all_packages:
    m = dup_pattern.match(pkg.slug)
    if m:
        base_slug = m.group(1)
        if base_slug in all_slugs:
            # Original exists — this is a duplicate
            original = Package.objects.filter(slug=base_slug).first()
            to_delete.append((pkg, original))

print(f'  Duplicates found: {bold(str(len(to_delete)))}')
for dup, orig in to_delete:
    has_bookings = Booking.objects.filter(package=dup).exists()
    booking_warn = red('  ⚠ HAS BOOKINGS — skipping') if has_bookings else ''
    print(f'  {red("✗ DELETE")} [{dup.id}] {dup.name}  (slug: {dup.slug})')
    print(f'           └─ original: [{orig.id}] {orig.slug}{booking_warn}')

# ── Step 2: Packages that are inactive but should be active ──────────────────
print(f'\n{cyan(bold("STEP 2 — Check which originals are inactive"))}')
print(SEP)

originals_inactive = []
for pkg in all_packages:
    m = dup_pattern.match(pkg.slug)
    if m:
        continue   # skip duplicates here
    if not pkg.is_active:
        # Only flag 2026 packages — Ramadhan 2025 can stay inactive
        if pkg.travel_date and pkg.travel_date.year >= 2026:
            originals_inactive.append(pkg)

if not originals_inactive:
    print(f'  {green("✓ All 2026 original packages are active.")}')
else:
    print(f'  {yellow(f"{len(originals_inactive)} 2026 original package(s) are inactive — will activate:")}')
    for p in originals_inactive:
        print(f'  {yellow("●")} [{p.id}] {p.name}')

# ── Step 3: Apply changes ────────────────────────────────────────────────────
print(f'\n{cyan(bold("STEP 3 — Apply changes"))}')
print(SEP)

if DRY_RUN:
    print(yellow('  DRY RUN — no changes applied.'))
    print(yellow('  Set DRY_RUN = False at the top of this script to apply.'))
else:
    deleted_count  = 0
    skipped_count  = 0
    activated_count = 0

    # Delete duplicates (skip any with bookings)
    for dup, orig in to_delete:
        has_bookings = Booking.objects.filter(package=dup).exists()
        if has_bookings:
            print(yellow(f'  SKIP (has bookings) [{dup.id}] {dup.slug}'))
            skipped_count += 1
            continue
        # Also delete associated room prices first
        RoomSharingPrice.objects.filter(package=dup).delete()
        dup.delete()
        deleted_count += 1
        print(green(f'  ✓ Deleted [{dup.id}] {dup.slug}'))

    # Activate inactive 2026 originals
    for p in originals_inactive:
        p.is_active = True
        p.save(update_fields=['is_active'])
        activated_count += 1
        print(green(f'  ✓ Activated [{p.id}] {p.name}'))

    print(f'\n  {green(f"Deleted:   {deleted_count} duplicate package(s)")}')
    if skipped_count:
        print(f'  {yellow(f"Skipped:   {skipped_count} (have bookings — check manually)")}')
    if activated_count:
        print(f'  {green(f"Activated: {activated_count} package(s)")}')

# ── Step 4: Final state ───────────────────────────────────────────────────────
print(f'\n{cyan(bold("STEP 4 — Final state after fix"))}')
print(SEP)

remaining = list(Package.objects.filter(is_active=True).order_by('travel_date'))
print(f'  Active packages in DB: {bold(str(len(remaining)))}')

print(f'\n  Checking live site...')
live_slugs = fetch_live_slugs()
if live_slugs:
    print(f'  Live site packages: {bold(str(len(live_slugs)))}')
    missing = [p for p in remaining if p.slug not in live_slugs]
    if not missing:
        print(green('  ✓ All active DB packages are now on the live site!'))
    else:
        print(yellow(f'  Still missing from live site: {len(missing)}'))
        for p in missing:
            print(f'    {yellow("●")} [{p.id}] {p.name}  (travel: {p.travel_date})')
        print()
        print(yellow('  Possible reasons for still missing packages:'))
        print(yellow('  · API pagination (site showing fewer than total)'))
        print(yellow('  · Category filter on frontend hiding some'))
        print(yellow('  · travel_date in the past being filtered by frontend'))

print()
print(bold('=' * 70))
print(bold('  DONE'))
print(bold('=' * 70))
print()
