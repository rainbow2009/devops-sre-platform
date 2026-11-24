import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.main import app, get_session
from app.models import SecurityControlRecord


@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(test_engine)

    with Session(test_engine) as session:
        session.add_all(
            [
                SecurityControlRecord(
                    id="IAM-001",
                    title="MFA for privileged accounts",
                    category="identity",
                ),
                SecurityControlRecord(
                    id="NET-001",
                    title="Public RDP exposure",
                    category="network",
                ),
                SecurityControlRecord(
                    id="BKP-001",
                    title="Backup freshness",
                    category="backup",
                ),
                SecurityControlRecord(
                    id="LOG-001",
                    title="Security log collection",
                    category="logging",
                ),
            ]
        )
        session.commit()

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        test_engine.dispose()


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "security-control-hub"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_schema(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Security Control Hub"


def test_list_controls(client):
    response = client.get("/api/v1/controls")
    assert response.status_code == 200
    assert len(response.json()) == 4


def test_controls_not_checked_by_default(client):
    response = client.get("/api/v1/controls")
    assert all(control["status"] == "not_checked" for control in response.json())


def test_get_control(client):
    response = client.get("/api/v1/controls/IAM-001")
    assert response.status_code == 200
    assert response.json()["category"] == "identity"


def test_control_not_found(client):
    response = client.get("/api/v1/controls/UNKNOWN")
    assert response.status_code == 404


def test_control_checks_empty(client):
    response = client.get("/api/v1/controls/BKP-001/checks")

    assert response.status_code == 200
    assert response.json() == []


def test_control_checks_unknown_control(client):
    response = client.get("/api/v1/controls/UNKNOWN/checks")

    assert response.status_code == 404


def test_control_checks_invalid_limit(client):
    response = client.get("/api/v1/controls/BKP-001/checks?limit=0")

    assert response.status_code == 422
