# AutoShkolla Platform — Backend

Flask + SQLAlchemy REST API for the AutoShkolla Platform, a multi-tenant driving school management SaaS for Kosovo.

The frontend lives in a separate repo: `autoshkolla-platform-frontend`.

## Stack

- Python 3.11+
- Flask 3 with custom `init_*` middleware (not Flask extensions)
- SQLAlchemy 2 + Flask-Migrate (Alembic)
- PostgreSQL 15+
- PyJWT for auth, Pydantic for validation
- WeasyPrint + Jinja2 for PDF generation
- pytest for tests
- Gunicorn for production WSGI

## Local development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # fill in real values
flask db upgrade
flask seed-locations       # one-time seed of Kosovo geographic data
python wsgi.py             # http://localhost:5002
```

## Tests

```bash
pytest -v --cov=app
```

## Production deploy (DigitalOcean App Platform)

This repo ships with a `Procfile` and `.do/app.yaml` so DigitalOcean App Platform can detect the build automatically.

1. Push this repo to GitHub.
2. In DigitalOcean → Apps → Create App, point at the GitHub repo.
3. Set environment variables (use `.env.example` as the checklist). At minimum:
   - `DATABASE_URL` — your managed Postgres connection string
   - `SECRET_KEY` — random secret
   - `JWT_SECRET` — random secret
   - `CORS_ORIGIN` — the Vercel URL of the frontend, e.g. `https://autoshkolla-platform.vercel.app`
   - `FLASK_ENV=production`
4. Add a managed Postgres database in the same App, attach it, and run migrations on first deploy.

Gunicorn binds to `$PORT` (DO injects it). The Procfile entrypoint is:

```
web: gunicorn --config gunicorn_config.py wsgi:app
```

## Architecture

See `docs/OVERVIEW.md` for the full architecture description, and `CLAUDE.md` for agent instructions.

## Modules

Tracked in `docs/MODULES_STATUS.md`. Database schema in `docs/DATABASE_SCHEMA.md`. API reference in `docs/API_REFERENCE.md`.
