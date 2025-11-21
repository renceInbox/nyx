### Troubleshooting

This page lists common problems and fixes when developing or running Nyx.

App won’t start / appears to hang
- Check background tasks or network calls. Nyx fetches JWKS on demand, not at startup, but verify you didn’t add startup I/O.
- Ensure the database is reachable and the URI uses `postgresql+asyncpg://`.

Alembic import errors
- Confirm `alembic.ini` contains `prepend_sys_path = src:.`.
- Ensure your models are imported by `config/db.py` so metadata is discoverable.

401/403 on protected routes
- Ensure the token’s `kid` is present in the JWKS at `config.zitadel.Settings.jwks_url`.
- Verify `aud` matches `config.zitadel.Settings.audience`.
- Check token validity period (iat/nbf/exp) and system clock.

Async driver mismatch
- Use `postgresql+asyncpg://` in `SQLALCHEMY_DATABASE_URI`.

OpenAPI docs missing
- Litestar may expose docs at `/schema` or `/docs` depending on configuration. Check server logs for the exact URL.

Tests fail due to network/JWKS
- Stub JWKS retrieval in tests, or point to a static JWKS that includes the signing key used for your test tokens.
