### Configuration

Nyx uses pydantic-settings and dotenv files under `.envs/` to load configuration. Defaults are safe for local development.

App settings (config/base.py)
- Class: `config.base.Settings`
- Key variable (case-insensitive env): `SQLALCHEMY_DATABASE_URI`
- Default: `postgresql+asyncpg://baseuser:password@localhost:5432/nyx`

Zitadel settings (config/zitadel.py)
- Class: `config.zitadel.Settings`
- Loads from `.envs/.zitadel` if present
- Defaults:
  - `ISSUER=http://localhost:8080`
  - `JWKS_URL=http://localhost:8080/oauth/v2/keys`
  - `AUDIENCE=347527518753980419`
  - `JWKS_REFRESH_INTERVAL=21600` (seconds)

Recommended dotenv files
- `.envs/.local`
```
SQLALCHEMY_DATABASE_URI=postgresql+asyncpg://<user>:<pass>@<host>:<port>/<db>
```
- `.envs/.zitadel`
```
ISSUER=https://<your-zitadel-domain>
JWKS_URL=https://<your-zitadel-domain>/oauth/v2/keys
AUDIENCE=<your-audience>
JWKS_REFRESH_INTERVAL=21600
```

Notes
- Ensure the database URI uses the async driver prefix `postgresql+asyncpg://`.
- In production, set environment variables via your orchestration platform rather than committing dotenv files.
