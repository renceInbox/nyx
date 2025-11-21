### Contributing

Thanks for your interest in improving Nyx! This guide outlines how to propose changes.

Prerequisites
- Python 3.13
- PostgreSQL available for local testing if you change DB-related code

Getting started
1) Fork the repository and create a feature branch:
```
git checkout -b feat/<short-description>
```
2) Install dependencies:
```
uv sync
# or
python -m pip install -e .
```
3) Configure local environment (optional):
```
mkdir -p .envs
echo "SQLALCHEMY_DATABASE_URI=postgresql+asyncpg://baseuser:password@localhost:5432/nyx" > .envs/.local
```

Coding standards
- Follow the existing import order and file layout. Keep modules small and focused.
- Use msgspec `Struct` for high-throughput internal DTOs where applicable (`src/schemas.py`).
- For external API schemas, prefer Litestar DTOs (`src/profiles/schemas.py`).
- Place business logic in services (`src/profiles/services.py`) and persistence in repositories (`src/profiles/repositories.py`).

Migrations
- After changing models, autogenerate a migration and review it:
```
alembic revision --autogenerate -m "<message>"
alembic upgrade head
```
Ensure your models are imported in `config/db.py` for autogenerate.

Testing
- Add or update tests under `tests/` (files named `test_*.py`).
- Run tests with:
```
python -m unittest discover -s tests -p 'test_*.py' -v
```
- For guarded routes, either supply a valid JWT and JWKS, or stub JWKS retrieval in tests.

Commit hygiene
- Keep commits small and focused; prefer descriptive messages.
- If you introduce tooling (e.g., pre-commit, pytest), document it in the README/docs.

Opening a Pull Request
- Describe the problem, solution, and any trade-offs.
- Include screenshots/logs for user-facing or operational changes when helpful.
- Note any migration steps or configuration changes required by operators.

License
- This project currently does not include an explicit license. Please open an issue to discuss licensing (e.g., MIT, Apache-2.0) before contributing significant code changes.
