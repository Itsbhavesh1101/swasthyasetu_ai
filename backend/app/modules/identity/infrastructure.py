"""SQLAlchemy identity records and identity-owned repository."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Uuid, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from app.modules.identity.domain import Actor, ActorStatus, ActorType, RoleCode
from app.shared.persistence import Base
from app.shared.types import OpaqueId


class ActorRecord(Base):
    __tablename__ = "actors"
    __table_args__ = (
        CheckConstraint(
            "actor_type IN ('PATIENT','PSEUDONYMOUS_USER','CAREGIVER','CLINICIAN',"
            "'COUNSELLOR','TRIAGE_STAFF','RESOURCE_ADMIN','CLINICAL_REVIEWER',"
            "'SYSTEM_ADMIN','RESEARCHER','SERVICE_ACCOUNT')",
            name="actor_type_supported",
        ),
        CheckConstraint("status IN ('ACTIVE','DISABLED')", name="status_supported"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    actor_type: Mapped[str] = mapped_column(String(32), nullable=False)
    subject_ref: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    institution_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=ActorStatus.ACTIVE.value,
        server_default=text("'ACTIVE'"),
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    role_records: Mapped[list["ActorRoleRecord"]] = relationship(
        back_populates="actor", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return (
            f"ActorRecord(id={self.id!r}, actor_type={self.actor_type!r}, status={self.status!r})"
        )


class ActorRoleRecord(Base):
    __tablename__ = "actor_roles"
    __table_args__ = (
        CheckConstraint(
            "role_code IN ('patient','pseudonymous_user','clinician','resource_admin',"
            "'clinical_reviewer','system_admin','researcher')",
            name="role_code_supported",
        ),
    )

    actor_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("actors.id", name="fk_actor_roles_actor_id_actors", ondelete="CASCADE"),
        primary_key=True,
    )
    role_code: Mapped[str] = mapped_column(String(32), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actor: Mapped[ActorRecord] = relationship(back_populates="role_records")


class PostgresActorRepository:
    async def create(
        self,
        session: AsyncSession,
        *,
        actor_id: OpaqueId,
        actor_type: ActorType,
        roles: frozenset[RoleCode],
        subject_id: OpaqueId | None,
        institution_id: OpaqueId | None,
        created_at: datetime,
    ) -> ActorRecord:
        record = ActorRecord(
            id=actor_id.value,
            actor_type=actor_type.value,
            subject_ref=None if subject_id is None else subject_id.value,
            institution_id=None if institution_id is None else institution_id.value,
            status=ActorStatus.ACTIVE.value,
            created_at=created_at,
            updated_at=created_at,
            role_records=[
                ActorRoleRecord(role_code=role.value, created_at=created_at)
                for role in sorted(roles, key=lambda value: value.value)
            ],
        )
        session.add(record)
        await session.flush()
        return record

    async def get(self, session: AsyncSession, actor_id: OpaqueId) -> ActorRecord | None:
        statement = (
            select(ActorRecord)
            .options(selectinload(ActorRecord.role_records))
            .where(ActorRecord.id == actor_id.value)
        )
        return (await session.execute(statement)).scalar_one_or_none()

    async def get_for_update(self, session: AsyncSession, actor_id: OpaqueId) -> ActorRecord | None:
        statement = (
            select(ActorRecord)
            .options(selectinload(ActorRecord.role_records))
            .where(ActorRecord.id == actor_id.value)
            .with_for_update()
        )
        return (await session.execute(statement)).scalar_one_or_none()

    def disable(self, record: object, *, disabled_at: object) -> Actor:
        if not isinstance(record, ActorRecord) or not isinstance(disabled_at, datetime):
            raise TypeError("identity repository received an unexpected value")
        record.status = ActorStatus.DISABLED.value
        record.updated_at = disabled_at
        return self.to_domain(record)

    def to_domain(self, record: object) -> Actor:
        if not isinstance(record, ActorRecord):
            raise TypeError("identity repository received an unexpected record")
        return Actor(
            actor_id=OpaqueId(record.id),
            actor_type=ActorType(record.actor_type),
            roles=frozenset(RoleCode(role.role_code) for role in record.role_records),
            subject_id=None if record.subject_ref is None else OpaqueId(record.subject_ref),
            institution_id=(
                None if record.institution_id is None else OpaqueId(record.institution_id)
            ),
            status=ActorStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
