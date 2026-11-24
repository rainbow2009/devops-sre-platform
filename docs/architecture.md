# Security Control Hub architecture

The Hub is a read-only HTTP API over a PostgreSQL control catalog and its recorded check results. Local development runs Uvicorn on the host and PostgreSQL 17 in Docker Compose. The database port binds to loopback, and a named volume stores the data between runs.

## Request flow

1. FastAPI routes in `app/main.py` validate request parameters and serialize the response using Pydantic models.
2. A database-backed request opens a SQLAlchemy session using the process's cached engine. The first engine request loads repository-root `.env` values as fallbacks for the process environment and builds a `postgresql+psycopg` URL. The pool checks connections before reuse.
3. The handler reads enabled control definitions and their check records. The request dependency closes the session on exit.

## Data model

| Table | Fields and constraints |
| --- | --- |
| `security_controls` | String control ID (primary key), title, category, optional description, and an enabled flag that defaults to true. |
| `control_checks` | Generated integer ID, control ID, result, source, optional note, and a timezone-aware check timestamp. A foreign key restricts deletion of controls with history. |

A control has zero or more checks. Stored results are `passed`, `failed`, `needs_review`, and `error`. The latest result is selected by descending check time with descending check ID as the tie-breaker. The API returns `not_checked` when there are no records. A recorded result remains current in the summary until a newer check arrives.

## HTTP endpoints

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/` | Reports the service name and running status. |
| GET | `/health` | Reports process liveness independently of the database. |
| GET | `/api/v1/controls` | Lists all enabled controls by ID, including title, category, and latest status. |
| GET | `/api/v1/controls/{control_id}` | Returns a single enabled control with the same fields. |
| GET | `/api/v1/controls/{control_id}/checks` | Lists check ID, control ID, result, source, note, and timestamp, newest first. The optional `limit` defaults to 50 and accepts 1 through 100. |

The detail and history routes return 404 for unknown or disabled controls. An enabled control without history returns an empty history list. FastAPI serves the OpenAPI schema at `/openapi.json` and interactive documentation at `/docs`.

## Schema and local data

Alembic uses the ORM metadata in `app/models.py` and the same PostgreSQL settings as the API. The initial revision `b4b2d2e471f9` creates both tables, their constraints, and an index on `control_checks.control_id`. The seed script inserts missing synthetic definitions in one transaction. Check histories start empty.

## Test boundary

The pytest fixture overrides the FastAPI session dependency and creates the ORM tables in an in-memory SQLite database. Importing the app and running these tests require no PostgreSQL settings. Alembic upgrades and PostgreSQL-specific behavior need separate integration checks.

See the [local setup instructions](../README.md) and [roadmap](../ROADMAP.md).
