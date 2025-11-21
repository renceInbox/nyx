### Database & Migrations

Nyx uses SQLAlchemy (via Advanced Alchemy) with an async PostgreSQL driver (`asyncpg`) and Alembic configured for asyncio.

Models and metadata discovery
- Models live under `src/profiles/models.py` (add more modules as you grow).
- `config/db.py` imports models to ensure SQLAlchemy metadata is discoverable by Alembic autogenerate. If you add models, import them there.

Connection URL
- Must use async driver: `postgresql+asyncpg://user:pass@host:port/dbname`
- Configure via `SQLALCHEMY_DATABASE_URI` (see docs/configuration.md).

Running migrations
```
alembic upgrade head
```

Creating a new migration after model changes
1) Update or add your models under `src/.../models.py`.
2) Ensure they’re imported from `config/db.py`.
3) Autogenerate a revision:
```
alembic revision --autogenerate -m "Describe your change"
```
4) Review the generated script under `migrations/versions/` and adjust as needed.
5) Apply it:
```
alembic upgrade head
```

Alembic configuration tips
- `alembic.ini` and `migrations/env.py` are set up with `prepend_sys_path = src:.` so imports like `from src.profiles.models import Profile` work in migration scripts.
- The env is configured for asyncio; avoid blocking operations in migration scripts.

Troubleshooting
- Import errors in Alembic: confirm `prepend_sys_path = src:.` in `alembic.ini` and that your models are imported by `config/db.py`.
- Async driver mismatch: ensure URLs use `postgresql+asyncpg://`.
