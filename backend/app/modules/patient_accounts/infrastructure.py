"""SQLAlchemy record owned by the patient account bounded context."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.persistence import Base


class PatientAccountRecord(Base):
    """Private local credential record bound to one actor and patient."""

    __tablename__ = "patient_accounts"
    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE','DISABLED')", name="status_supported"),
        CheckConstraint(
            "email_normalized = lower(btrim(email_normalized))",
            name="email_normalized_canonical",
        ),
        CheckConstraint(
            "length(btrim(email_display)) > 0 AND length(btrim(display_name)) > 0",
            name="display_fields_nonempty",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    actor_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("actors.id", name="fk_patient_accounts_actor_id_actors"),
        unique=True,
        nullable=False,
    )
    patient_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("patients.id", name="fk_patient_accounts_patient_id_patients"),
        unique=True,
        nullable=False,
    )
    email_normalized: Mapped[str] = mapped_column(
        String(320), nullable=False, unique=True, index=True
    )
    email_display: Mapped[str] = mapped_column(String(320), nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return (
            f"PatientAccountRecord(id={self.id!r}, actor_id={self.actor_id!r}, "
            f"patient_id={self.patient_id!r}, status={self.status!r})"
        )
