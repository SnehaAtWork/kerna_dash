import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base import Base, TimestampMixin


class ProjectModule(Base, TimestampMixin):
    __tablename__ = "project_modules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    module_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="NOT_STARTED")
    internal_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # relationships
    project: Mapped["Project"] = relationship("Project", back_populates="modules")
    assignments: Mapped[list["ModuleAssignment"]] = relationship("ModuleAssignment", back_populates="module", cascade="all, delete-orphan")
    versions: Mapped[list["ModuleVersion"]] = relationship("ModuleVersion", back_populates="module")


class ModuleAssignment(Base):
    __tablename__ = "module_assignments"
    __table_args__ = (UniqueConstraint("module_id", "user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("project_modules.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # relationships
    module: Mapped["ProjectModule"] = relationship("ProjectModule", back_populates="assignments")
    user: Mapped["User"] = relationship("User")


class ModuleVersion(Base, TimestampMixin):
    __tablename__ = "module_versions"
    __table_args__ = (UniqueConstraint("module_id", "version_number"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("project_modules.id", ondelete="RESTRICT"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    file_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # relationships
    module: Mapped["ProjectModule"] = relationship("ProjectModule", back_populates="versions")
    approvals: Mapped[list["Approval"]] = relationship("Approval", back_populates="version")
    uploader: Mapped["User"] = relationship("User")


class Approval(Base, TimestampMixin):
    __tablename__ = "approvals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("module_versions.id", ondelete="RESTRICT"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    lock_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    withdrawn_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    # relationships
    version: Mapped["ModuleVersion"] = relationship("ModuleVersion", back_populates="approvals")