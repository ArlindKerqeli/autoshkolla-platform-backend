"""
Import candidates from Excel files into AutoShkolla Pro database.

Sources:
  1. migration-data-rina-2025.xlsx — 5,054 historical candidates (1995–2025)
     Columns: Emri, Mbiemri, Gjinia, NumriPersonal, Datelindja, Nr Protokolit,
              Kategoria, Data e regjistrimti, Kom Vendlindja, Vendlindja,
              Kom Vendbanimi, Vendbanimi, Telefoni

  2. Lista e kandiateve.xls — 232 active candidates with payment data
     Columns: Nr, Kandidati, Kategoria, Ore (T/P), Nr.Personal, Telefoni,
              Vendbanimi, Regjistruar me, Cmimi, Paguar, Borxhi

Strategy:
  - Import ALL candidates from file 2 (migration data) as the primary source
    (has richer data: gender, DOB, birth/residence locations, protocol number)
  - Enrich with payment data from file 1 (Lista) where personal numbers match
  - Candidates only in file 1 get imported with what data we have
  - Candidates with registrations before 2025-08-01 are marked as archived
  - Candidates appearing multiple times (different categories) create
    supplementary_registrations for older entries, keep latest as primary
  - Missing places are auto-created under their municipality
  - Foreign birth places (non-Kosovo) use birth_place_foreign field

Usage:
  cd backend
  source venv/bin/activate
  python ../scripts/import_candidates.py [--dry-run] [--tenant-slug SLUG]

Options:
  --dry-run       Show what would be imported without writing to DB
  --tenant-slug   Target tenant slug (default: "autoshkolla-rina")
"""

import argparse
import os
import sys
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal
from pathlib import Path
from collections import defaultdict

import xlrd
import openpyxl

# Add backend to path so we can import the Flask app
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / 'backend'
sys.path.insert(0, str(BACKEND_DIR))

from app import create_app
from app.utils.db import db
from app.models.candidate_model import Candidate
from app.models.category_model import Category
from app.models.country_model import Country
from app.models.municipality_model import Municipality
from app.models.place_model import Place
from app.models.supplementary_registration_model import SupplementaryRegistration


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EXCEL_EPOCH = datetime(1899, 12, 30)  # Excel serial date base

# Category defaults (theory_hours / practical_hours / price)
CATEGORY_DEFAULTS = {
    'B':  {'theory_hours': 20, 'practical_hours': 20, 'price': Decimal('350.00')},
    'C':  {'theory_hours': 15, 'practical_hours': 15, 'price': Decimal('0.00')},
    'CE': {'theory_hours': 15, 'practical_hours': 0,  'price': Decimal('0.00')},
    'D':  {'theory_hours': 15, 'practical_hours': 15, 'price': Decimal('0.00')},
}

# Birth municipality corrections (lowercase/misspelled -> proper municipality)
BIRTH_MUNICIPALITY_FIXES = {
    'kaqanik': 'Kaçanik',
    'greme': 'Ferizaj',      # Greme is a village in Ferizaj municipality
    'koshare': 'Ferizaj',    # Koshare is a village in Ferizaj area
    'softaj': 'Ferizaj',     # Softaj is a village in Ferizaj municipality
    'varosh': 'Ferizaj',     # Varosh is a neighborhood in Ferizaj
}

# Archive cutoff — candidates registered before this date are archived
ARCHIVE_CUTOFF = date(2025, 8, 1)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def excel_serial_to_date(serial: float) -> date | None:
    """Convert Excel serial number to Python date."""
    if not serial or serial == 0:
        return None
    try:
        return (EXCEL_EPOCH + timedelta(days=int(serial))).date()
    except (ValueError, OverflowError):
        return None


def normalize_category(raw: str) -> str | None:
    """Normalize category code to uppercase, filter invalid values."""
    if not raw:
        return None
    cleaned = raw.strip().upper()
    if cleaned in ('B', 'C', 'CE', 'D', 'BD'):
        return cleaned
    if cleaned in ('-', ''):
        return 'B'  # Default to B for unknown/missing categories
    return None


def normalize_name(name: str) -> str:
    """Clean up name: strip, title case, remove double spaces."""
    if not name:
        return ''
    return ' '.join(name.strip().split()).title()


def split_full_name(full_name: str) -> tuple[str, str]:
    """Split 'FIRST LAST' into (first_name, last_name)."""
    parts = full_name.strip().split()
    if len(parts) >= 2:
        return normalize_name(parts[0]), normalize_name(' '.join(parts[1:]))
    elif len(parts) == 1:
        return normalize_name(parts[0]), ''
    return '', ''


def clean_phone(phone: str) -> str | None:
    """Clean phone number, return None if empty/placeholder."""
    if not phone:
        return None
    cleaned = phone.strip()
    if cleaned in ('-', ' ', '', 'None'):
        return None
    return cleaned


def parse_hours(hours_str: str) -> tuple[int, int]:
    """Parse 'T / P' hours string, e.g. '20 / 20' -> (20, 20)."""
    if not hours_str or '/' not in str(hours_str):
        return 20, 20
    parts = str(hours_str).split('/')
    try:
        return int(parts[0].strip()), int(parts[1].strip())
    except (ValueError, IndexError):
        return 20, 20


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_migration_data(filepath: str) -> list[dict]:
    """Load candidates from migration-data-rina-2025.xlsx."""
    wb = openpyxl.load_workbook(filepath, data_only=True)
    sheet = wb['Sheet1']
    rows = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        first_name = normalize_name(str(row[0])) if row[0] else ''
        last_name = normalize_name(str(row[1])) if row[1] else ''
        gender = str(row[2]).strip().upper() if row[2] else None
        personal_number = str(row[3]).strip() if row[3] else ''
        dob = row[4].date() if isinstance(row[4], datetime) else None
        protocol_number = str(row[5]).strip() if row[5] else None
        category = normalize_category(str(row[6]) if row[6] else '')
        reg_date = row[7].date() if isinstance(row[7], datetime) else None
        birth_muni = str(row[8]).strip() if row[8] else ''
        birth_place = str(row[9]).strip() if row[9] else ''
        res_muni = str(row[10]).strip() if row[10] else ''
        res_place = str(row[11]).strip() if row[11] else ''
        phone = clean_phone(str(row[12]) if row[12] else '')

        if not personal_number or not first_name or not last_name:
            continue

        if gender not in ('M', 'F'):
            gender = None

        if protocol_number in ('-', '', 'None'):
            protocol_number = None

        rows.append({
            'first_name': first_name,
            'last_name': last_name,
            'gender': gender,
            'personal_number': personal_number,
            'date_of_birth': dob,
            'protocol_number': protocol_number,
            'category': category,
            'registration_date': reg_date,
            'birth_municipality': birth_muni,
            'birth_place': birth_place,
            'residence_municipality': res_muni,
            'residence_place': res_place,
            'phone': phone,
            'source': 'migration',
        })

    return rows


def load_active_candidates(filepath: str) -> list[dict]:
    """Load candidates from Lista e kandiateve.xls."""
    wb = xlrd.open_workbook(filepath)
    sheet = wb.sheet_by_name('rptKandidatetLista')
    rows = []

    for row_idx in range(12, sheet.nrows):
        row = [sheet.cell_value(row_idx, col_idx) for col_idx in range(sheet.ncols)]

        # Skip empty/totals rows
        personal_number = str(row[6]).strip() if row[6] else ''
        if not personal_number or not row[2]:
            continue

        first_name, last_name = split_full_name(str(row[2]))
        category = normalize_category(str(row[3]))
        theory_hours, practical_hours = parse_hours(str(row[5]))
        phone = clean_phone(str(row[8]) if row[8] else '')
        municipality = str(row[11]).strip() if row[11] else ''
        reg_date = excel_serial_to_date(row[13])
        price = Decimal(str(row[14])) if row[14] else Decimal('0')
        amount_paid = Decimal(str(row[15])) if row[15] else Decimal('0')

        rows.append({
            'first_name': first_name,
            'last_name': last_name,
            'personal_number': personal_number,
            'category': category,
            'theory_hours': theory_hours,
            'practical_hours': practical_hours,
            'phone': phone,
            'residence_municipality': municipality,
            'registration_date': reg_date,
            'price': price,
            'amount_paid': amount_paid,
            'source': 'active_list',
        })

    return rows


# ---------------------------------------------------------------------------
# Location resolution
# ---------------------------------------------------------------------------

class LocationResolver:
    """Resolve municipality/place names to database UUIDs, creating missing places."""

    def __init__(self, tenant_id: uuid.UUID, dry_run: bool = False):
        self.tenant_id = tenant_id
        self.dry_run = dry_run
        self._municipality_cache: dict[str, Municipality] = {}
        self._place_cache: dict[tuple[str, str], Place | None] = {}
        self._kosovo_id: uuid.UUID | None = None
        self._other_country_id: uuid.UUID | None = None
        self._known_municipalities: set[str] = set()
        self._places_created = 0
        self._next_place_code = 10000  # Start auto-created place codes at 10000
        self._load_caches()

    def _load_caches(self):
        """Preload all municipalities and places from DB."""
        kosovo = Country.query.filter_by(code='KS').first()
        other = Country.query.filter_by(code='OTHER').first()
        self._kosovo_id = kosovo.id if kosovo else None
        self._other_country_id = other.id if other else None

        for muni in Municipality.query.all():
            self._municipality_cache[muni.name.lower()] = muni
            self._known_municipalities.add(muni.name)

        for place in Place.query.all():
            muni = self._municipality_cache.get(
                next((m.name.lower() for m in Municipality.query.filter_by(id=place.municipality_id).all()), ''),
                None
            )
            if muni:
                self._place_cache[(muni.name.lower(), place.name.lower())] = place

        # Reload place cache more efficiently
        self._place_cache = {}
        all_places = db.session.query(Place, Municipality).join(
            Municipality, Place.municipality_id == Municipality.id
        ).all()
        for place, muni in all_places:
            self._place_cache[(muni.name.lower(), place.name.lower())] = place

        # Find max place code for auto-increment
        max_code = db.session.query(db.func.max(Place.code)).scalar()
        if max_code and max_code >= self._next_place_code:
            self._next_place_code = max_code + 1

    def resolve_municipality(self, name: str) -> Municipality | None:
        """Find municipality by name (case-insensitive, with fixes)."""
        if not name or name == '-':
            return None

        # Apply known fixes
        fixed = BIRTH_MUNICIPALITY_FIXES.get(name.lower(), name)
        return self._municipality_cache.get(fixed.lower())

    def resolve_place(self, municipality_name: str, place_name: str) -> Place | None:
        """Find place by municipality + place name, creating if needed."""
        if not place_name or place_name in ('-', ' ', ''):
            return None

        muni = self.resolve_municipality(municipality_name)
        if not muni:
            return None

        # Try exact match
        key = (muni.name.lower(), place_name.lower().strip())
        if key in self._place_cache:
            return self._place_cache[key]

        # Try title case match
        key_title = (muni.name.lower(), normalize_name(place_name).lower())
        if key_title in self._place_cache:
            return self._place_cache[key_title]

        # Create missing place
        if not self.dry_run:
            new_place = Place(
                municipality_id=muni.id,
                name=normalize_name(place_name),
                code=self._next_place_code,
            )
            db.session.add(new_place)
            db.session.flush()
            self._place_cache[key] = new_place
            self._place_cache[key_title] = new_place
            self._next_place_code += 1
            self._places_created += 1
            return new_place

        self._places_created += 1
        return None

    def is_foreign_birth(self, municipality_name: str) -> bool:
        """Check if the birth municipality is outside Kosovo."""
        if not municipality_name or municipality_name == '-':
            return False
        fixed = BIRTH_MUNICIPALITY_FIXES.get(municipality_name.lower(), municipality_name)
        return fixed.lower() not in self._municipality_cache


# ---------------------------------------------------------------------------
# Import logic
# ---------------------------------------------------------------------------

def generate_candidate_code(index: int) -> str:
    """Generate candidate code like CAND-0001."""
    return f'CAND-{index:04d}'


def run_import(tenant_slug: str, dry_run: bool = False):
    """Main import function."""
    app = create_app()

    with app.app_context():
        # Resolve tenant
        from app.models.tenant_model import Tenant
        tenant = Tenant.query.filter_by(slug=tenant_slug).first()
        if not tenant:
            print(f'ERROR: Tenant with slug "{tenant_slug}" not found.')
            print('Available tenants:')
            for t in Tenant.query.all():
                print(f'  - {t.slug} ({t.name})')
            sys.exit(1)

        tenant_id = tenant.id
        print(f'Target tenant: {tenant.name} (id={tenant_id})')
        print(f'Mode: {"DRY RUN" if dry_run else "LIVE IMPORT"}')
        print()

        # Resolve categories (create if missing)
        category_map: dict[str, Category] = {}
        for cat_code, defaults in CATEGORY_DEFAULTS.items():
            cat = Category.query.filter_by(tenant_id=tenant_id, code=cat_code).first()
            if not cat:
                if not dry_run:
                    cat = Category(
                        tenant_id=tenant_id,
                        code=cat_code,
                        description=f'Kategoria {cat_code}',
                        theory_hours=defaults['theory_hours'],
                        practical_hours=defaults['practical_hours'],
                        price=defaults['price'],
                        is_licensed=True,
                        is_active=True,
                    )
                    db.session.add(cat)
                    db.session.flush()
                print(f'{"Will create" if dry_run else "Created"} category: {cat_code}')
            if cat:
                category_map[cat_code] = cat
            elif dry_run:
                # In dry-run mode, use a placeholder so counting works
                category_map[cat_code] = True  # placeholder

        # Location resolver
        resolver = LocationResolver(tenant_id, dry_run=dry_run)

        # Load data from both files
        migration_file = str(PROJECT_ROOT / 'migration-data-rina-2025.xlsx')
        active_file = str(PROJECT_ROOT / 'Lista e kandiateve.xls')

        print('Loading migration data...')
        migration_rows = load_migration_data(migration_file)
        print(f'  Loaded {len(migration_rows)} rows from migration file')

        print('Loading active candidates...')
        active_rows = load_active_candidates(active_file)
        print(f'  Loaded {len(active_rows)} rows from active list')
        print()

        # Build lookup by personal_number for active list
        active_by_pn: dict[str, dict] = {}
        for row in active_rows:
            active_by_pn[row['personal_number']] = row

        # Group migration rows by personal_number (same person, multiple categories)
        migration_by_pn: dict[str, list[dict]] = defaultdict(list)
        for row in migration_rows:
            migration_by_pn[row['personal_number']].append(row)

        # Sort each person's registrations by date (latest first)
        for pn in migration_by_pn:
            migration_by_pn[pn].sort(
                key=lambda r: r['registration_date'] or date.min,
                reverse=True
            )

        # Collect all personal numbers (union of both files)
        all_personal_numbers = set(migration_by_pn.keys()) | set(active_by_pn.keys())

        # Check for existing candidates in DB
        existing_pns = set()
        existing = Candidate.query.filter_by(tenant_id=tenant_id).all()
        for c in existing:
            existing_pns.add(c.personal_number)

        print(f'Existing candidates in DB: {len(existing_pns)}')
        print(f'Unique candidates to process: {len(all_personal_numbers)}')

        # Stats
        stats = {
            'imported': 0,
            'supplementary': 0,
            'skipped_existing': 0,
            'skipped_no_category': 0,
            'errors': 0,
        }

        code_counter = len(existing) + 1  # Continue from existing candidates

        for pn in sorted(all_personal_numbers):
            if pn in existing_pns:
                stats['skipped_existing'] += 1
                continue

            migration_entries = migration_by_pn.get(pn, [])
            active_entry = active_by_pn.get(pn)

            # Determine primary registration (latest entry)
            # Priority: active list entry (most current), then latest migration entry
            primary = None
            supplementary_entries = []

            if active_entry and migration_entries:
                # Use migration data for rich fields, active for payment data
                primary_migration = migration_entries[0]  # Latest migration entry
                primary = {**primary_migration}

                # Override with active list data (payment info, current category)
                primary['category'] = active_entry.get('category') or primary['category']
                primary['price'] = active_entry.get('price', Decimal('0'))
                primary['amount_paid'] = active_entry.get('amount_paid', Decimal('0'))
                primary['theory_hours'] = active_entry.get('theory_hours', CATEGORY_DEFAULTS.get(primary['category'], {}).get('theory_hours', 20))
                primary['practical_hours'] = active_entry.get('practical_hours', CATEGORY_DEFAULTS.get(primary['category'], {}).get('practical_hours', 20))
                primary['phone'] = active_entry.get('phone') or primary.get('phone')
                primary['registration_date'] = active_entry.get('registration_date') or primary.get('registration_date')
                primary['is_active'] = True

                # All migration entries become supplementary (previous registrations)
                supplementary_entries = migration_entries[1:] if len(migration_entries) > 1 else []
                # If the primary migration entry has a different category than active,
                # it's also supplementary
                if primary_migration.get('category') and primary_migration['category'] != primary['category']:
                    supplementary_entries = migration_entries  # All migration entries are older
            elif migration_entries:
                # Only in migration data
                primary = migration_entries[0]
                primary['price'] = CATEGORY_DEFAULTS.get(primary.get('category', ''), {}).get('price', Decimal('0'))
                primary['amount_paid'] = Decimal('0')
                primary['is_active'] = False
                supplementary_entries = migration_entries[1:]
            elif active_entry:
                # Only in active list (no migration data)
                primary = active_entry.copy()
                primary['gender'] = None
                primary['date_of_birth'] = None
                primary['birth_municipality'] = ''
                primary['birth_place'] = ''
                primary['residence_place'] = ''
                primary['protocol_number'] = None
                primary['is_active'] = True

            if not primary:
                continue

            cat_code = primary.get('category')
            if not cat_code or cat_code not in category_map:
                stats['skipped_no_category'] += 1
                continue

            category = category_map[cat_code]
            cat_defaults = CATEGORY_DEFAULTS.get(cat_code, {})

            # Determine archive status
            reg_date = primary.get('registration_date') or date.today()
            is_archived = not primary.get('is_active', False) or reg_date < ARCHIVE_CUTOFF

            # Resolve locations
            # Birth location
            birth_country_id = None
            birth_municipality_id = None
            birth_place_id = None
            birth_municipality_foreign = None
            birth_place_foreign = None

            birth_muni_name = primary.get('birth_municipality', '')
            birth_place_name = primary.get('birth_place', '')

            if birth_muni_name and not resolver.is_foreign_birth(birth_muni_name):
                birth_country_id = resolver._kosovo_id
                muni = resolver.resolve_municipality(birth_muni_name)
                if muni:
                    birth_municipality_id = muni.id
                    if birth_place_name:
                        place = resolver.resolve_place(birth_muni_name, birth_place_name)
                        if place:
                            birth_place_id = place.id
            elif birth_place_name:
                birth_country_id = resolver._other_country_id
                birth_municipality_foreign = birth_muni_name or None
                birth_place_foreign = birth_place_name

            # Residence location
            residence_municipality_id = None
            residence_place_id = None

            res_muni_name = primary.get('residence_municipality', '')
            res_place_name = primary.get('residence_place', '')

            if res_muni_name:
                res_muni = resolver.resolve_municipality(res_muni_name)
                if res_muni:
                    residence_municipality_id = res_muni.id
                    if res_place_name:
                        res_place = resolver.resolve_place(res_muni_name, res_place_name)
                        if res_place:
                            residence_place_id = res_place.id

            # Build candidate code
            candidate_code = generate_candidate_code(code_counter)

            try:
                if not dry_run:
                    candidate = Candidate(
                        tenant_id=tenant_id,
                        code=candidate_code,
                        first_name=primary['first_name'],
                        last_name=primary['last_name'],
                        personal_number=pn,
                        phone=primary.get('phone'),
                        gender=primary.get('gender'),
                        date_of_birth=primary.get('date_of_birth'),
                        birth_country_id=birth_country_id,
                        birth_municipality_id=birth_municipality_id,
                        birth_place_id=birth_place_id,
                        birth_municipality_foreign=birth_municipality_foreign,
                        birth_place_foreign=birth_place_foreign,
                        residence_municipality_id=residence_municipality_id,
                        residence_place_id=residence_place_id,
                        category_id=category.id,
                        price=primary.get('price', cat_defaults.get('price', Decimal('0'))),
                        amount_paid=primary.get('amount_paid', Decimal('0')),
                        theory_hours=primary.get('theory_hours', cat_defaults.get('theory_hours', 20)),
                        practical_hours=primary.get('practical_hours', cat_defaults.get('practical_hours', 20)),
                        registration_date=reg_date,
                        protocol_number=primary.get('protocol_number'),
                        is_archived=is_archived,
                    )
                    db.session.add(candidate)
                    db.session.flush()

                # Count and create supplementary registrations for older entries
                for supp in supplementary_entries:
                    supp_cat_code = supp.get('category')
                    if not supp_cat_code or supp_cat_code not in category_map:
                        continue

                    if not dry_run:
                        supp_cat = category_map[supp_cat_code]
                        supp_defaults = CATEGORY_DEFAULTS.get(supp_cat_code, {})
                        supp_reg = SupplementaryRegistration(
                            candidate_id=candidate.id,
                            tenant_id=tenant_id,
                            category_id=supp_cat.id,
                            is_automatic=False,
                            price=supp_defaults.get('price', Decimal('0')),
                            practical_hours=supp_defaults.get('practical_hours', 20),
                            theory_hours=supp_defaults.get('theory_hours', 20),
                            registration_date=supp.get('registration_date') or reg_date,
                        )
                        db.session.add(supp_reg)

                    stats['supplementary'] += 1

                stats['imported'] += 1
                code_counter += 1

            except Exception as e:
                stats['errors'] += 1
                print(f'  ERROR importing {pn} ({primary["first_name"]} {primary["last_name"]}): {e}')
                if not dry_run:
                    db.session.rollback()
                continue

        # Commit
        if not dry_run:
            db.session.commit()
            print('Database committed successfully.')
        print()

        # Report
        print('=' * 60)
        print('IMPORT SUMMARY')
        print('=' * 60)
        print(f'  Candidates imported:        {stats["imported"]}')
        print(f'  Supplementary registrations: {stats["supplementary"]}')
        print(f'  Skipped (already in DB):    {stats["skipped_existing"]}')
        print(f'  Skipped (no valid category): {stats["skipped_no_category"]}')
        print(f'  Errors:                     {stats["errors"]}')
        print(f'  New places created:         {resolver._places_created}')
        print()

        if dry_run:
            print('This was a DRY RUN. No data was written to the database.')
            print('Remove --dry-run to perform the actual import.')


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import candidates from Excel files')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview import without writing to database',
    )
    parser.add_argument(
        '--tenant-slug',
        default='autoshkolla-rina',
        help='Target tenant slug (default: autoshkolla-rina)',
    )
    args = parser.parse_args()

    run_import(tenant_slug=args.tenant_slug, dry_run=args.dry_run)
