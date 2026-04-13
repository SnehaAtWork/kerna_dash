import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base import Base, TimestampMixin


class Client(Base, TimestampMixin):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    primary_contact_name: Mapped[str] = mapped_column(String(255), nullable=False)
    primary_email: Mapped[str] = mapped_column(String(255), nullable=False)
    primary_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    poc_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    client_view_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="BALANCED")

    # relationships
    poc_user: Mapped["User"] = relationship("User")
    client_users: Mapped[list["ClientUser"]] = relationship("ClientUser", back_populates="client", cascade="all, delete-orphan")
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="client", cascade="all, delete-orphan")


class ClientUser(Base, TimestampMixin):
    __tablename__ = "client_users"
    __table_args__ = (UniqueConstraint("client_id", "email"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # relationships
    client: Mapped["Client"] = relationship("Client", back_populates="client_users")


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False, index=True)
    project_type_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="INITIATED")
    internal_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    client_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    health_score_internal: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    health_status_client: Mapped[str] = mapped_column(String(20), nullable=False, default="ON_TRACK")
    maintenance_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    maintenance_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    change_request_window_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # relationships
    client: Mapped["Client"] = relationship("Client", back_populates="projects")
    modules: Mapped[list["ProjectModule"]] = relationship("ProjectModule", back_populates="project", cascade="all, delete-orphan")
    # add to Project relationships
    invoices: Mapped[list["Invoice"]] = relationship("Invoice", back_populates="project")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="project")
    resources: Mapped[list["Resource"]] = relationship("Resource", back_populates="project")