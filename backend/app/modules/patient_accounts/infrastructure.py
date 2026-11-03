"""SQLAlchemy record owned by the patient account bounded context."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Uuid, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.patient_accounts.contracts import AccountAlreadyExistsError
from app.modules.patient_accounts.domain import (
    AccountStatus,
    DisplayName,
    EmailAddress,
    PasswordDigest,
    PatientAccount,
)
from app.shared.persistence import Base
from app.shared.types import OpaqueId


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


class PostgresPatientAccountRepository:
    """Transaction-scoped private account persistence."""

    async def add(self, session: AsyncSession, account: PatientAccount) -> PatientAccountRecord:
        record = PatientAccountRecord(
            id=account.account_id.value,
            actor_id=account.actor_id.value,
            patient_id=account.patient_id.value,
            email_normalized=account.email.normalized,
            email_display=account.email.display,
            display_name=account.display_name.value,
            password_hash=account.password_digest.value,
            status=account.status.value,
            created_at=account.created_at,
            updated_at=account.updated_at,
        )
        session.add(record)
        try:
            await session.flush()
        except IntegrityError as error:
            if _constraint_name(error) in {
                "ix_patient_accounts_email_normalized",
                "uq_patient_accounts_actor_id",
                "uq_patient_accounts_patient_id",
            }:
                raise AccountAlreadyExistsError from error
            raise
        return record

    async def get_by_email(
        self, session: AsyncSession, email_normalized: str
    ) -> PatientAccount | None:
        statement = select(PatientAccountRecord).where(
            PatientAccountRecord.email_normalized == email_normalized
        )
        record = (await session.execute(statement)).scalar_one_or_none()
        return None if record is None else self.to_domain(record)

    async def get_by_actor(
        self, session: AsyncSession, actor_id: OpaqueId
    ) -> PatientAccount | None:
        statement = select(PatientAccountRecord).where(
            PatientAccountRecord.actor_id == actor_id.value
        )
        record = (await session.execute(statement)).scalar_one_or_none()
        return None if record is None else self.to_domain(record)

    @staticmethod
    def to_domain(record: PatientAccountRecord) -> PatientAccount:
        return PatientAccount(
            account_id=OpaqueId(record.id),
            actor_id=OpaqueId(record.actor_id),
            patient_id=OpaqueId(record.patient_id),
            email=EmailAddress(record.email_display),
            display_name=DisplayName(record.display_name),
            password_digest=PasswordDigest.from_persisted(record.password_hash),
            status=AccountStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
        )


def _constraint_name(error: IntegrityError) -> str | None:
    diagnostic = getattr(error.orig, "diag", None)
    return None if diagnostic is None else getattr(diagnostic, "constraint_name", None)
