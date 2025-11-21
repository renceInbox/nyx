Nyx Service
===========

High-performance ASGI service built with Litestar, SQLAlchemy (via Advanced Alchemy), and PostgreSQL. This repository includes JWT-based authentication against Zitadel, async database access with `asyncpg`, and clean layering for controllers, services, and repositories.

Quick links
- Docs home: docs/ — index of all guides in this repository
- Getting started: docs/getting-started.md — install, configure, migrate, and run locally
- Configuration: docs/configuration.md — environment variables and dotenv files
- Auth (JWT/JWKS via Zitadel): docs/auth.md — how authentication and guards work
- Zitadel local guide: docs/zitadel.md — run Zitadel locally, log in, create a client, get tokens
- Database & migrations (Alembic): docs/database-and-migrations.md — manage models and generate/apply migrations
- Testing: docs/testing.md — run tests and patterns for unit/integration tests
- Troubleshooting: docs/troubleshooting.md — fixes for common issues
- Contributing: CONTRIBUTING.md — workflow and standards for changes

Features
- Litestar ASGI app with OpenAPI and global Bearer security
- Async PostgreSQL via `asyncpg` and SQLAlchemy 2.x (Advanced Alchemy)
- JWT Auth with JWKS caching (Zitadel defaults)
- Profiles domain example (controller, service, repository, DTOs)
- Alembic migrations configured for asyncio
- Typed DTOs with msgspec and Litestar DTOs where appropriate

Stack
- Python 3.13
- Litestar, SQLAlchemy (Advanced Alchemy), Alembic
- msgspec, pydantic-settings
- PostgreSQL (async) w/ `asyncpg`

Repository layout
```
alembic.ini
config/
  base.py        # App settings (pydantic-settings)
  db.py          # Engine/session and model imports for metadata discovery
  zitadel.py     # Zitadel/OpenID configuration
migrations/      # Alembic (async) env and revisions
src/
  main.py        # Litestar app entrypoint: src.main:app
  guards.py      # jwt_guard using JWKS with caching
  profiles/      # Example domain (controllers, schemas, services, repos, models)
```

Quickstart
1) Install (use uv or pip)
```
uv sync
# or
python -m pip install -e .
```

2) Configure environment (optional — defaults provided)
Create `.envs/.local` and `.envs/.zitadel` if you need custom values. See docs/configuration.md.

3) Run database migrations
```
alembic upgrade head
```

4) Start the app
```
litestar --app src.main:app run --debug --reload
```

5) OpenAPI docs
- Visit http://localhost:8000/schema or the interactive docs under `/schema` (Litestar configuration may expose `/schema` or `/docs`).
- Protected endpoints require `Authorization: Bearer <token>`.

Development notes
- Background task runs to refresh JWKS periodically (see `src.utils.refresh_jwks_periodically`).
- All `profiles` routes are guarded by `jwt_guard`. For local inspection only, you may temporarily remove the guard from `ProfileController` but do not commit such a change.

Testing
```
python -m unittest discover -s tests -p 'test_*.py' -v
```
See docs/testing.md for patterns and examples.

Contributing
See CONTRIBUTING.md. Issues and PRs are welcome. Please follow the code style and testing guidelines.

License
This project is licensed under the PolyForm Noncommercial License 1.0.0. You may use, copy, and modify the software for noncommercial purposes. Commercial use requires a separate commercial license. See the LICENSE file for details or open an issue to discuss commercial licensing.
