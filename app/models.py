from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class SecurityControlRecord(Base):
    __tablename__ = "security_controls"

    id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
    )

    title: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    checks: Mapped[list["ControlCheckRecord"]] = relationship(
        back_populates="control",
    )


class ControlCheckRecord(Base):
    __tablename__ = "control_checks"

    __table_args__ = (
        CheckConstraint(
            "status IN ('passed', 'failed', 'needs_review', 'error')",
            name="valid_control_status",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )

    control_id: Mapped[str] = mapped_column(
        ForeignKey("security_controls.id", ondelete="RESTRICT"),
        index=True,
    )

    status: Mapped[str] = mapped_column(String(20))
    source: Mapped[str] = mapped_column(String(100))
    note: Mapped[str | None] = mapped_column(Text)

    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    control: Mapped[SecurityControlRecord] = relationship(
        back_populates="checks",
    )
