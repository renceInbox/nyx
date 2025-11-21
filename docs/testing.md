### Testing

Nyx does not mandate a specific test framework. Python’s builtin `unittest` works out of the box.

Run tests
```
python -m unittest discover -s tests -p 'test_*.py' -v
```

Add a new test
- Create files under `tests/` named `test_*.py`.
- Use standard `unittest` style. You may use `pytest` if you add it to your environment, but it’s not required by the project.

Async tests tips
- Prefer pure unit tests that don’t require network/DB.
- If you need DB-backed tests, use a separate ephemeral PostgreSQL and set `SQLALCHEMY_DATABASE_URI` accordingly so you don’t clobber local data.

Guarded routes
- Routes under `src/profiles/controllers.py` are protected by `jwt_guard`.
- For integration tests, either:
  - Provide a valid `Authorization: Bearer <token>` and configure `config.zitadel` to point to a JWKS with the signing key; or
  - Patch/stub the JWKS retrieval so your tests use a static key set.

Minimal sanity test example
```
import unittest

from config.base import Settings
from config.zitadel import Settings as ZitadelSettings
from src.schemas import CurrentUser


class SanityTests(unittest.TestCase):
    def test_base_settings_defaults(self):
        s = Settings()
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

Best practices
- Keep tests fast and deterministic.
- Isolate I/O behind small abstractions so you can stub them (e.g., pass an `httpx.AsyncClient` or a `get_jwks` callable to the component that needs network).
