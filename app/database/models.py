from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Customer(Base):
	__tablename__ = "customers"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	name: Mapped[str] = mapped_column(String(120), nullable=False)
	phone: Mapped[str | None] = mapped_column(String(30), nullable=True, unique=True)
	email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	conversations = relationship("Conversation", back_populates="customer")
	appointments = relationship("Appointment", back_populates="customer")


class Conversation(Base):
	__tablename__ = "conversations"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	session_id: Mapped[str] = mapped_column(String(120), index=True)
	customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
	)

	customer = relationship("Customer", back_populates="conversations")
	messages = relationship(
		"Message", back_populates="conversation", cascade="all, delete-orphan"
	)


class Message(Base):
	__tablename__ = "messages"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), index=True)
	role: Mapped[str] = mapped_column(String(20), nullable=False)
	content: Mapped[str] = mapped_column(Text, nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	conversation = relationship("Conversation", back_populates="messages")


class ServiceCatalog(Base):
	__tablename__ = "service_catalog"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
	description: Mapped[str | None] = mapped_column(Text, nullable=True)
	price_inr: Mapped[float | None] = mapped_column(Float, nullable=True)
	duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

	appointments = relationship("Appointment", back_populates="service")


class Appointment(Base):
	__tablename__ = "appointments"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
	service_id: Mapped[int | None] = mapped_column(
		ForeignKey("service_catalog.id"), nullable=True
	)
	starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
	ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
	status: Mapped[str] = mapped_column(String(40), default="pending")
	notes: Mapped[str | None] = mapped_column(Text, nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	customer = relationship("Customer", back_populates="appointments")
	service = relationship("ServiceCatalog", back_populates="appointments")
