from sqlalchemy.orm import Session

from app.db import get_engine
from app.models import SecurityControlRecord

DEMO_CONTROLS = [
    {
        "id": "IAM-001",
        "title": "MFA for privileged accounts",
        "category": "identity",
    },
    {
        "id": "NET-001",
        "title": "Public RDP exposure",
        "category": "network",
    },
    {
        "id": "BKP-001",
        "title": "Backup freshness",
        "category": "backup",
    },
    {
        "id": "LOG-001",
        "title": "Security log collection",
        "category": "logging",
    },
]


def main():
    # This script is intended only for the local development database.
    engine = get_engine()
    if (
        engine.url.host not in ("localhost", "127.0.0.1")
        or engine.url.database != "security_control_hub"
    ):
        raise RuntimeError("Refusing to seed a non-local demo database")

    inserted = 0

    with Session(engine) as session, session.begin():
        for data in DEMO_CONTROLS:
            existing = session.get(
                SecurityControlRecord,
                data["id"],
            )

            if existing is None:
                session.add(SecurityControlRecord(**data))
                inserted += 1

    print(f"Inserted {inserted} demo security controls")


if __name__ == "__main__":
    main()
