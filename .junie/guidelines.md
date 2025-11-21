Nyx project — developer guidelines

This document captures project-specific knowledge needed to build, run, test, and extend the Nyx service. It assumes you are an experienced Python developer; it omits generic info and focuses on the particulars of this codebase.

Overview
- Frameworks: Litestar (ASGI), SQLAlchemy (via Advanced Alchemy), Alembic, msgspec, pydantic-settings.
- App entrypoint: `src.main:app` (Litestar application).
- AuthN/AuthZ: Bearer JWT validated against Zitadel JWKS; all `profiles` routes are guarded.
- DB: PostgreSQL (async) using `asyncpg` driver.

Build, setup, and configuration
1) Python and dependencies
- Python: 3.13 (see `pyproject.toml`).
- Install deps with your preferred tool, for example:
  - uv: `uv sync` (preferred when `uv.lock` is present) or `uv pip install -r <(uv pip compile pyproject.toml)`
  - pip: `python -m pip install -e .` (PEP 621) or `python -m pip install -r requirements.txt` if you maintain one locally.

2) Environment configuration
- App settings (`config/base.py`):
  - Source: pydantic-settings; `.envs/.local` (relative to repo root) is loaded if present.
  - Key variable: `SQLALCHEMY_DATABASE_URI` (case-insensitive) maps to `Settings.sqlalchemy_database_uri`.
  - Default: `postgresql+asyncpg://baseuser:password@localhost:5432/nyx`.
- Zitadel settings (`config/zitadel.py`):
  - Source: `.envs/.zitadel` if present.
  - Defaults: `issuer=http://localhost:8080`, `jwks_url=http://localhost:8080/oauth/v2/keys`, `audience=347527518753980419`, `jwks_refresh_interval=21600` (6h).
- Create local env files as needed:
  - `.envs/.local`:
    - `SQLALCHEMY_DATABASE_URI=postgresql+asyncpg://<user>:<pass>@<host>:<port>/<db>`
  - `.envs/.zitadel`:
    - `ISSUER=...`
    - `JWKS_URL=...`
    - `AUDIENCE=...`

3) Database and migrations
- Alembic is configured for asyncio + Advanced Alchemy (`alembic.ini`, `migrations/env.py`).
- Path and discovery are set up with `prepend_sys_path = src:.` so imports like `from src.profiles.models import Profile` resolve in migrations.
- Typical flow:
  - Ensure DB is reachable and the URI matches the async driver (`postgresql+asyncpg://...`).
  - Upgrade: `alembic upgrade head`.
  - Autogenerate a revision (if you change models):
    - `alembic revision --autogenerate -m "<message>"`
    - Inspect/clean the generated script under `migrations/versions/` before applying.

Running the application
- ASGI app: `src.main:app`.
- Start with uvicorn (or any ASGI server):
  - `uvicorn src.main:app --reload --port 8000`
- OpenAPI is configured with a global Bearer security scheme; interactive docs will expect an `Authorization: Bearer <token>` header for protected endpoints.
- Background tasks: on startup `src.utils.refresh_jwks_periodically()` runs in a task to refresh JWKS according to `config/zitadel.Settings.jwks_refresh_interval`.

Auth and guards
- All `profiles` endpoints (`src/profiles/controllers.py`) are protected with `guards = [jwt_guard]`.
- The guard (`src/guards.py`) fetches JWKS from `config.zitadel.zitadel_settings.jwks_url` on demand and caches keys for `_ttl = 3600` seconds.
- To call protected endpoints in dev:
  - Ensure a Zitadel instance is reachable at the configured `jwks_url`, or
  - Provide a JWT signed with a key whose `kid` is present in the JWKS.
- If you only need to inspect the app locally without auth, you may temporarily remove the guard from `ProfileController` during development. Do not commit such a change.

Testing: configuring and running
The repository does not mandate a specific test runner; the simplest zero-dependency option is Python’s builtin `unittest` discovery.

- Run all tests with unittest discovery:
  - `python -m unittest discover -s tests -p 'test_*.py' -v`
- Add a new test:
  - Place files under `tests/` named `test_*.py`.
  - Use standard `unittest` or `pytest` style if you decide to add pytest (not currently listed in dependencies).
- Async tests:
  - Prefer to isolate pure units that don’t require network/DB.
  - If you need DB-backed tests, use an ephemeral Postgres (e.g., docker) and a separate test DB URI via `SQLALCHEMY_DATABASE_URI` environment variable to avoid clobbering local data.
- Integration tests for guarded routes:
  - When exercising routes protected by `jwt_guard`, provide a valid `Authorization` header and configure `config/zitadel` values to point to a JWKS that contains the signing key (`kid` must match). Alternatively, patch `JWKSCache.get_keys` in tests to return a static set of keys.

Test example that was verified locally
We validated the following minimal test using `python -m unittest -q` before updating this document. It illustrates how to structure tests without external services. Note: this example was used transiently for verification and removed afterward as per repository hygiene; you can recreate it under `tests/` to run locally.

```
import unittest

from config.base import Settings
from config.zitadel import Settings as ZitadelSettings
from src.schemas import CurrentUser


class SanityTests(unittest.TestCase):
    def test_base_settings_defaults(self):
        s = Settings()  # reads from .envs/.local if present; otherwise defaults
        # The default URI uses asyncpg driver; adjust if you change config/base.py
        self.assertTrue(s.sqlalchemy_database_uri.startswith("postgresql+asyncpg://"))

    def test_zitadel_settings_defaults(self):
        zs = ZitadelSettings()
        self.assertTrue(zs.jwks_url.startswith("http://"))
        self.assertGreaterEqual(zs.jwks_refresh_interval, 3600)

    def test_current_user_struct_defaults(self):
        u = CurrentUser(sub="user-123")
        self.assertEqual(u.sub, "user-123")
        self.assertIsInstance(u.roles, list)


if __name__ == "__main__":
    unittest.main()
```

Guidelines for adding more tests
- Keep unit tests pure and fast; prefer deterministic units over network-bound code.
- For code that does I/O or network (e.g., JWKS fetch), prefer dependency inversion:
  - Add a thin indirection (e.g., pass an `httpx.AsyncClient` or a `get_jwks` callable) so tests can stub it.
- Use factory helpers for domain objects to simplify DTO/service tests; see `src/profiles/schemas.py` for DTO/Struct patterns.

Project-specific tips and conventions
- Code style
  - Follow the existing imports and layout; keep modules small and focused.
  - Use msgspec `Struct` for high-throughput typed data in request context or internal DTOs where applicable (`src/schemas.py`).
  - For external API schemas and request/response validation, use Litestar DTOs defined under `src/profiles/schemas.py`.
- Services and repositories
  - Business logic belongs in `services` (e.g., `src/profiles/services.py`) using Advanced Alchemy services.
  - Repositories (`src/profiles/repositories.py`) encapsulate persistence operations and query patterns.
- Migrations and models
  - Always import models in `config/db.py` to ensure metadata discovery (note the `# noqa` import of `Profile`). If you add models, ensure they are imported for Alembic autogenerate to see them.
- OpenAPI and security
  - `src.main` configures a global Bearer security requirement. When adding new controllers, they inherit the global security, but you can override at the handler level if needed.
- Background tasks
  - Long-lived loops like `refresh_jwks_periodically` should honor a configurable interval; consider making the interval injectable for tests.

Common issues and troubleshooting
- Import errors in Alembic: confirm `alembic.ini` has `prepend_sys_path = src:.` and that your migrations import models via `from src.<...> import ...`.
- Async driver mismatch: ensure URLs use `postgresql+asyncpg://` for async engines.
- 401/403 on protected routes:
  - Check that your token’s `kid` exists in the JWKS at `zitadel_settings.jwks_url` and that `aud` matches `zitadel_settings.audience`.
- Hanging startup in dev: if the app silently “hangs”, check background tasks or network calls (e.g., JWKS fetch) that may be blocked by proxies. The current code only fetches JWKS on demand, not at startup, but verify any additions you make don’t introduce startup I/O.

Release and dependency hygiene
- Prefer pinning via `uv lock` to keep `uv.lock` up-to-date.
- Keep `pre-commit` hooks consistent with the team’s setup; this repo lists the dependency but does not include a config file. If you add one, document the policy here.

Updating this document
- Keep commands exact and validated. If you change configs or process, update examples and re-verify they work.
