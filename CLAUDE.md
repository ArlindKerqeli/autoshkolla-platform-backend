# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

**autoshkolla-platform-backend** — Flask 3 + SQLAlchemy 2 + PyJWT REST API for AutoShkolla Platform, a multi-tenant driving school management SaaS for Kosovo. Deploys to DigitalOcean App Platform.

The Next.js frontend lives in a separate sibling repo, **autoshkolla-platform-frontend**. The parent folder `~/Desktop/autoshkolla-platform/` is not itself a git repo — it just holds the two child repos side by side, with a top-level `CLAUDE.md` covering the cross-repo workspace.

## Tech stack

- Python 3.11+, Flask 3 (`create_app()` factory + custom `init_*` middleware, **not** Flask extensions for cross-cutting concerns)
- SQLAlchemy 2.0 + Flask-Migrate (Alembic) on PostgreSQL 15+
- **PyJWT** for auth — custom encode/decode helpers in `app/utils/jwt.py`, NOT Flask-JWT-Extended
- **Pydantic 2** for request/response validation (`BaseSchema` with `extra='forbid'` in `app/utils/validation.py`)
- **WeasyPrint** + Jinja2 for PDF generation
- bcrypt for password hashing, Flask-CORS for cross-origin
- pytest (+ pytest-cov, factory-boy) for unit/integration; Playwright invoked separately for E2E
- Gunicorn for production WSGI
- **No Docker**. Python venv directly.

## Architecture (poolgo-ops pattern)

- `create_app()` factory in `app/__init__.py` wires the **middleware chain** in this order: `init_db` → `init_request_id` → `init_auth_context` → `init_api_auth_guard` → `init_response_envelope` → `init_error_handlers`, then registers the single `api_bp` Blueprint at `/api/v1`.
- **Single Blueprint** (`api_bp` in `app/api/__init__.py`) — every route module (`auth.py`, `candidates.py`, …) is imported there as a side-effect. There are no sub-blueprints.
- **Layered**: routes → services (business logic) → models. Routes are thin; logic lives in `app/services/`.
- **Tenant context** is request-scoped on Flask's `g`: `auth_context` middleware decodes the JWT (from `Authorization` header OR cookie) and sets `g.current_user` + `g.tenant_id`. `api_auth_guard` enforces auth on `/api/v1/*` except a `PUBLIC_PATHS` allowlist.
- **Response envelope**: every success response is auto-wrapped as `{"success": true, "data": ...}`. Custom exceptions (`ValidationError`, `Unauthorized`, `Forbidden`, `NotFound`) in `middleware/error_handler.py` map to HTTP status codes automatically.
- **JSON serialization**: UUIDs and datetimes are handled by `app.json.default = json_default` (set in `create_app`).
- **Request parsing**: use `parse_body(SchemaClass)` / `parse_query(SchemaClass)` from `app/utils/validation.py` — never read `request.get_json()` raw.

## Multi-tenancy (mandatory)

- Every tenant-scoped model has a non-nullable `tenant_id` UUID FK. Use the `TenantMixin` base class.
- Every query MUST filter by `g.tenant_id`. Never expose data across tenants.
- **Exceptions** (shared reference data, no `tenant_id`): `country`, `municipality`, `place`, `lesson_chapter`. Seeded once via `flask seed-locations`.

## Project layout

```
autoshkolla-platform-backend/
├── CLAUDE.md                       # this file
├── DEVELOPMENT_PLAN.md             # original full feature spec
├── README.md
├── Procfile                        # web: gunicorn --config gunicorn_config.py wsgi:app
├── gunicorn_config.py
├── runtime.txt                     # python-3.11.x
├── requirements.txt
├── wsgi.py                         # python wsgi.py → :5002
├── .env.example                    # checklist of required env vars
├── .do/app.yaml                    # DigitalOcean App Platform spec
├── app/
│   ├── __init__.py                 # create_app() — middleware chain + blueprint registration
│   ├── config.py                   # Single Config class reading env vars
│   ├── api/                        # All HTTP routes — every file is imported by api/__init__.py
│   │   ├── __init__.py             # api_bp Blueprint + side-effect imports
│   │   ├── health.py               # GET /health
│   │   ├── auth.py                 # login, refresh, logout, me
│   │   ├── locations.py            # countries / municipalities / places (shared ref data)
│   │   ├── school.py, categories.py, instructors.py, vehicles.py
│   │   ├── candidates.py           # core CRUD
│   │   ├── theory_hours.py, practical_hours.py, lesson_chapters.py
│   │   ├── payments.py, expenses.py, verifications.py, exams.py
│   │   ├── scheduled_lessons.py    # calendar / lesson scheduling
│   │   ├── messages.py             # instructor ↔ admin threaded messaging
│   │   ├── instructor_portal.py    # instructor-only endpoints
│   │   ├── instructor_payments.py  # 65€/candidate debt tracking
│   │   ├── dashboard.py            # admin dashboard metrics aggregator
│   │   ├── print_docs.py           # PDF generation endpoints
│   │   ├── users.py, superadmin.py, exports.py
│   ├── schemas/                    # Pydantic request/response schemas, one file per module
│   ├── services/                   # Business logic (auth, candidate, instructor, exam, export)
│   ├── models/                     # SQLAlchemy models — one per file, suffixed `_model.py`
│   ├── middleware/                 # init_* functions (auth_context, api_auth_guard, error_handler, response_envelope, request_id)
│   ├── utils/                      # db, jwt, validation (BaseSchema/parse_body), serialization, pagination
│   ├── pdf/                        # WeasyPrint PDF generation
│   │   ├── templates/              # Jinja2 HTML per document type
│   │   ├── styles/                 # pdf_base.css
│   │   └── assets/                 # Kosovo coat of arms, logos
│   └── seeds/                      # CLI seed commands: seed_locations, seed_users
├── migrations/                     # Alembic
├── migrations_raw/                 # legacy SQL dumps
├── scripts/
│   ├── import_candidates.py        # one-time legacy candidate import
│   └── init_schema.sql
├── tests/
│   ├── conftest.py
│   ├── unit/, integration/, e2e/
├── data/                           # seed CSVs / fixtures
└── docs/                           # source-of-truth docs, keep up to date
    ├── OVERVIEW.md, DATABASE_SCHEMA.md, API_REFERENCE.md
    ├── MODULES_STATUS.md, CHANGELOG.md
    ├── PDF_TEMPLATES.md, UI_DESIGN_GUIDELINES.md, SMS_NOTIFICATIONS.md
    ├── pdf-reference/              # screenshots of legacy PDFs for fidelity comparison
    └── ui-reference/               # screenshots of legacy UI
```

## Commands

```bash
# Setup (first time)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                # then fill values

# Database
flask db upgrade                    # apply pending Alembic migrations
flask db migrate -m "describe"      # generate a new migration (review before committing)
flask db downgrade -1               # roll back one revision
flask seed-locations                # one-time seed of countries / municipalities / places
flask seed-users                    # seed initial users (super-admin etc.)

# Run dev server (port 5002, NOT 5000)
python wsgi.py

# Tests
pytest -v --cov=app                                       # all tests + coverage
pytest tests/unit/test_candidate_model.py                 # single file
pytest tests/integration/test_candidates.py::test_create  # single test
pytest -k "candidate and not slow"                        # keyword filter

# Legacy candidate import (one-off)
python scripts/import_candidates.py --tenant-slug autoshkolla-demo --dry-run
python scripts/import_candidates.py --tenant-slug autoshkolla-demo

# Production (DigitalOcean injects $PORT)
gunicorn --config gunicorn_config.py wsgi:app
```

## Code conventions

- Type hints on every function signature.
- **One model per file** in `app/models/`, named `{name}_model.py` (e.g. `candidate_model.py`). Class name without the `_model` suffix.
- **Pydantic schemas** in `app/schemas/{module}.py` — strict (`extra='forbid'`), call via `parse_body(Schema)` / `parse_query(Schema)`.
- **Business logic in `app/services/`**, never inside route handlers. Routes parse + validate + call service + return.
- **Tenant filter**: always include `.filter_by(tenant_id=g.tenant_id)` (or use the tenant-scoped query helpers).
- **Database**: snake_case columns, UUID primary keys, `created_at`/`updated_at` on every table, `deleted_at` for soft-delete where applicable. Indexes on `tenant_id`, FKs, and frequently filtered columns. Dates stored UTC.
- **API URLs**: `/api/v1/{resource}` plural (e.g. `/api/v1/candidates`).
- **Date display format** (in PDFs / serialized output where the frontend expects it): `dd.MM.yyyy`. Currency: Euro (€).
- **Auth**: PyJWT only. Access + refresh tokens. Use the helpers in `app/utils/jwt.py`; don't import `jwt` directly into route code.

## PDF generation (100% fidelity required)

PDFs **must be visually identical** to the legacy system's output — they are official documents (some are Kosovo government forms).

- Engine: WeasyPrint + Jinja2.
- Templates: `app/pdf/templates/{document_type}.html`. Shared CSS: `app/pdf/styles/pdf_base.css`. Assets: `app/pdf/assets/`.
- Seven document types: **Fatura** (invoice), **Fleteparaqitja** (registration form, government), **Libreza** (logbook), **Kontrata** (contract), **Testi** (test result), **Vertetimi** (certificate, government), **Candidate List**.
- Government forms (Fleteparaqitja, Vertetimi) need the Kosovo coat of arms and trilingual headers.
- Albanian characters (`ë`, `ç`) must render correctly — use DejaVu Sans or equivalent.
- Date `dd.MM.yyyy`, currency `€`.
- Visually verify against `docs/pdf-reference/` before marking any PDF template complete.
- Full spec: `docs/PDF_TEMPLATES.md`.

## Permissions & roles

- Roles on `users.role`: `super_admin`, `admin`, `lecturer` (lecturer = ligjerues), `instructor`.
- **Instructors are read-only on candidates**: they may view candidates assigned to them, but never create / edit / delete. Enforce in service layer.
- When an instructor is created with email + password, auto-create a `users` row with `role='instructor'` and link via `instructor.user_id`.
- **Instructor debt model**: assigning a candidate to an instructor auto-creates an `instructor_payments` row at `instructor.cost_per_candidate` (default 65€). Admin records payments to reduce the balance.
- **Scheduled lessons**: marking a `scheduled_lessons` row `completed` auto-creates a `practical_hour_sessions` row. Statuses: `scheduled`, `completed`, `cancelled`, `no_show`.
- **Super-admin** can manage all tenants and impersonate users; super-admins are not allowed onto the regular tenant dashboard — they must impersonate to view tenant data.

## CORS, env, deploy

- Required env (see `.env.example`): `DATABASE_URL`, `SECRET_KEY`, `JWT_SECRET`, `CORS_ORIGIN` (comma-separated allowed origins — prod Vercel URL, preview, localhost), `FLASK_ENV`.
- `Config.cors_origins()` parses `CORS_ORIGIN` into a list. Flask-CORS allows credentials and exposes `X-Request-Id`.
- Deploy: DigitalOcean App Platform detects via `Procfile` + `.do/app.yaml`. Gunicorn binds `$PORT`. After deploy, the **frontend's Vercel URL must be in `CORS_ORIGIN`** and the backend URL (with `/api/v1` suffix) must be in the frontend's `NEXT_PUBLIC_API_URL`.

## Documentation discipline

After every change that touches schema, API, or modules, update the relevant doc(s):

- `docs/DATABASE_SCHEMA.md` — schema changes
- `docs/API_REFERENCE.md` — endpoint additions / changes
- `docs/MODULES_STATUS.md` — module completion %
- `docs/CHANGELOG.md` — dated entry per change
- `docs/PDF_TEMPLATES.md` — PDF template changes

## Module dependency graph

Modules 1–16, must be built in dependency order:

```
1 (Auth)         →  no deps
2 (Locations)    →  1
3 (School)       →  1, 2
4 (Categories)   →  1
5 (Instructors)  →  1
6 (Vehicles)     →  1, 5
7 (Candidates)   →  1, 2, 4, 5, 6
8 (Theory Hrs)   →  7
9 (Practical)    →  7, 5
10 (Payments)    →  7
11 (Verification)→  7, 8, 9
12 (Expenses)    →  1, 6
13 (Users)       →  1
14 (PDF Gen)     →  7, 8, 9, 11
15 (Super Admin) →  1
16 (Dashboard)   →  1
```

Module status tracked in `docs/MODULES_STATUS.md`.

## Albanian UI glossary (reference when generating API field names, error messages displayed to users, or PDF templates)

Although code is English, all user-facing strings (PDF labels, validation messages returned to the UI) are Albanian. Common terms:

```
Kandidatet=Candidates · Instruktor=Instructor · Ligjerues=Lecturer · Automjetet=Vehicles
Shpenzimet=Expenses · Pagesat=Payments · Kategoria=Category · Borxhi=Debt
Ore Teorike=Theory Hours · Ore Praktike=Practical Hours · Ore Plotesuese=Supplementary Hours
Vërtetimi=Certificate · Fatura=Invoice · Fletëparaqitja=Registration Form
Libreza=Logbook · Kontrata=Contract · Testi=Test · Arkiva=Archive
Evidenca Oreve=Hours Evidence · Provimet=Exams · Cilesimet=Settings
Mesazhet=Messages · Kalendari=Calendar · Paneli=Dashboard · Alarmet=Alerts
Kerko=Search · Registro=Register · Ruaj=Save · Mbyll=Close · Anulo=Cancel · Fshi=Delete · Edito=Edit · Paguaj=Pay
```
