### Getting Started

This guide helps you install, configure, migrate the database, and run the Nyx service locally.

Prerequisites
- Python 3.13
- PostgreSQL accessible locally or remotely

1) Clone and enter the repo
```
git clone <your-fork-or-origin> nyx
cd nyx
```

2) Install dependencies
- Preferred (uv):
```
uv sync
```
- Or with pip:
```
python -m pip install -e .
```

3) Configure environment (optional)
Defaults will work, but you can override using dotenv files. Create files under `.envs/` as needed.
- `.envs/.local`:
```
SQLALCHEMY_DATABASE_URI=postgresql+asyncpg://<user>:<pass>@<host>:<port>/<db>
```
- `.envs/.zitadel`:
```
ISSUER=http://localhost:8080
JWKS_URL=http://localhost:8080/oauth/v2/keys
AUDIENCE=347527518753980419
```

4) Initialize/upgrade the database
```
alembic upgrade head
```

5) Run the app (ASGI)
```
litestar --app src.main:app run --debug --reload
```
Optional (using uvx without installing litestar globally):
```
uvx litestar --app src.main:app run --debug --reload
```

6) Explore the API
- Open the interactive docs (OpenAPI) at `/schema` or `/docs` depending on Litestar config.
- Protected endpoints require `Authorization: Bearer <token>`.

Next steps
- Read docs/configuration.md for detailed settings.
- Read docs/auth.md to set up JWT/JWKS with Zitadel.
- See docs/database-and-migrations.md for model changes and migrations.
