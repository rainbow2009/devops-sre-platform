# Security Control Hub

Security Control Hub is a read-only FastAPI service for monitoring infrastructure security controls. It lists enabled controls, reports their latest recorded result, and serves check history. The local demo seeds four synthetic controls covering identity, network access, backups, and logging.

> [!WARNING]
> The API currently has no authentication or authorization. Use it only for local development with synthetic data. Never expose it publicly or use it with real company evidence.

## Install the Python environment

Run these commands from the repository root in a Linux or WSL shell with Python 3.12 and its `venv` module installed.

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

The development requirements include the application, Alembic, the test client, pytest, and Ruff. For an application-only environment, install `requirements.txt`.

## Run tests and lint

```sh
python -m pytest -q
ruff check .
```

The API tests use an in-memory SQLite database and can run immediately after installation. Docker, PostgreSQL credentials, and a local `.env` file are optional for these checks.

## Start the local API with PostgreSQL

1. Install Docker with a Compose version that supports `docker compose up --wait`. From the repository root, create a local configuration file if you do not already have one.

   ```sh
   test -e .env || cp .env.example .env
   ```

   For a new database, set `POSTGRES_DB=security_control_hub`, choose a local `POSTGRES_USER`, and replace the password placeholder with a private development password. For an existing database, keep its current credentials. The API and Alembic use `POSTGRES_HOST` (default `127.0.0.1`) and `POSTGRES_PORT` (default `5432`). Exported environment variables take precedence over the file.

2. Start PostgreSQL 17, wait for its health check, and apply the outstanding migrations.

   ```sh
   docker compose up -d --wait db
   python -m alembic upgrade head
   ```

3. Seed the local demo and start FastAPI from the activated virtual environment.

   ```sh
   python -m scripts.seed_controls
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

   The seed inserts missing control definitions and preserves existing rows on a rerun. It accepts the database name `security_control_hub` on `127.0.0.1` or `localhost`. On a fresh database, the seeded controls show `not_checked` and have empty histories.

4. Open the [interactive API documentation](http://127.0.0.1:8000/docs), or check the running service from a second terminal.

   ```sh
   curl http://127.0.0.1:8000/health
   curl http://127.0.0.1:8000/api/v1/controls
   ```

Stop Uvicorn with Ctrl+C. Use `docker compose stop db` to stop PostgreSQL and retain its named volume.

## Project documentation

- [Architecture and endpoint reference](docs/architecture.md)
- [Development roadmap](ROADMAP.md)
- [Development environment](docs/environment.md)
