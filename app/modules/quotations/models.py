# app/modules/quotations/models.py

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base import Base, TimestampMixin


class Quotation(Base, TimestampMixin):
    __tablename__ = "quotations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="RESTRICT"), nullable=False, index=True)
    poc_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT")
    template_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # relationships
    lead: Mapped["Lead"] = relationship("Lead", back_populates="quotations")
    poc: Mapped["User"] = relationship("User")
    versions: Mapped[list["QuotationVersion"]] = relationship("QuotationVersion", back_populates="quotation")


class QuotationVersion(Base, TimestampMixin):
    __tablename__ = "quotation_versions"
    __table_args__ = (UniqueConstraint("quotation_id", "version_number"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quotation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("quotations.id", ondelete="RESTRICT"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    subtotal: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    discount: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    total: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    is_final: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # relationships
    quotation: Mapped["Quotation"] = relationship("Quotation", back_populates="versions")
    line_items: Mapped[list["QuotationLineItem"]] = relationship("QuotationLineItem", back_populates="version", cascade="all, delete-orphan")


class QuotationLineItem(Base):
    __tablename__ = "quotation_line_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quotation_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("quotation_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    total: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)

    # relationships
    version: Mapped["QuotationVersion"] = relationship("QuotationVersion", back_populates="line_items")