from datetime import datetime
from enum import StrEnum
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_engine
from app.models import ControlCheckRecord, SecurityControlRecord


class ControlStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"
    ERROR = "error"
    NOT_CHECKED = "not_checked"


class SecurityControl(BaseModel):
    id: str
    title: str
    category: str
    status: ControlStatus


app = FastAPI(
    title="Security Control Hub",
    description="Infrastructure security control and evidence platform",
    version="0.1.0",
)


def get_session():
    with Session(get_engine()) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def serialize_control(
    control: SecurityControlRecord,
    session: Session,
) -> SecurityControl:
    latest_status = session.scalar(
        select(ControlCheckRecord.status)
        .where(ControlCheckRecord.control_id == control.id)
        .order_by(
            ControlCheckRecord.checked_at.desc(),
            ControlCheckRecord.id.desc(),
        )
        .limit(1)
    )

    return SecurityControl(
        id=control.id,
        title=control.title,
        category=control.category,
        status=(
            ControlStatus(latest_status)
            if latest_status is not None
            else ControlStatus.NOT_CHECKED
        ),
    )


@app.get("/")
def root():
    return {
        "service": "security-control-hub",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get(
    "/api/v1/controls",
    response_model=list[SecurityControl],
)
def list_controls(session: SessionDep):
    controls = session.scalars(
        select(SecurityControlRecord)
        .where(SecurityControlRecord.enabled.is_(True))
        .order_by(SecurityControlRecord.id)
    ).all()

    return [serialize_control(control, session) for control in controls]


@app.get(
    "/api/v1/controls/{control_id}",
    response_model=SecurityControl,
)
def get_control(control_id: str, session: SessionDep):
    control = session.get(SecurityControlRecord, control_id)

    if control is None or not control.enabled:
        raise HTTPException(
            status_code=404,
            detail="Control not found",
        )

    return serialize_control(control, session)


class ControlCheckRead(BaseModel):
    id: int
    control_id: str
    status: ControlStatus
    source: str
    note: str | None
    checked_at: datetime


@app.get(
    "/api/v1/controls/{control_id}/checks",
    response_model=list[ControlCheckRead],
)
def list_control_checks(
    control_id: str,
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
):
    control = session.get(SecurityControlRecord, control_id)

    if control is None or not control.enabled:
        raise HTTPException(
            status_code=404,
            detail="Control not found",
        )

    checks = session.scalars(
        select(ControlCheckRecord)
        .where(ControlCheckRecord.control_id == control_id)
        .order_by(
            ControlCheckRecord.checked_at.desc(),
            ControlCheckRecord.id.desc(),
        )
        .limit(limit)
    ).all()

    return [
        ControlCheckRead(
            id=check.id,
            control_id=check.control_id,
            status=ControlStatus(check.status),
            source=check.source,
            note=check.note,
            checked_at=check.checked_at,
        )
        for check in checks
    ]
