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
