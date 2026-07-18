import json
import os
from datetime import datetime, timedelta

import requests
from sqlalchemy.orm import Session

from app.database.models import Appointment, Customer, ServiceCatalog


def _normalize_phone(phone: str) -> str:
	return "".join(ch for ch in phone if ch.isdigit() or ch == "+")


def _find_or_create_customer(db: Session, name: str, phone: str) -> Customer:
	customer = db.query(Customer).filter(Customer.phone == phone).first()
	if customer:
		if customer.name != name:
			customer.name = name
			db.commit()
			db.refresh(customer)
		return customer

	customer = Customer(name=name, phone=phone)
	db.add(customer)
	db.commit()
	db.refresh(customer)
	return customer


def _find_or_create_service(db: Session, service_name: str) -> ServiceCatalog:
	service = (
		db.query(ServiceCatalog)
		.filter(ServiceCatalog.name.ilike(service_name.strip()))
		.first()
	)
	if service:
		return service

	service = ServiceCatalog(name=service_name.strip())
	db.add(service)
	db.commit()
	db.refresh(service)
	return service


def _has_conflict(db: Session, starts_at: datetime, ends_at: datetime) -> bool:
	conflict = (
		db.query(Appointment)
		.filter(Appointment.status.in_(["pending", "confirmed"]))
		.filter(Appointment.starts_at < ends_at)
		.filter(Appointment.ends_at > starts_at)
		.first()
	)
	return conflict is not None


def _find_next_available_slot(
	db: Session,
	preferred_slot: datetime,
	duration_minutes: int,
	search_attempts: int = 24,
) -> tuple[datetime, datetime] | None:
	for i in range(search_attempts):
		candidate_start = preferred_slot + timedelta(minutes=30 * i)
		candidate_end = candidate_start + timedelta(minutes=duration_minutes)
		if not _has_conflict(db, candidate_start, candidate_end):
			return candidate_start, candidate_end
	return None


def _send_booking_sms(phone: str, message: str) -> tuple[bool, str]:
	account_sid = os.getenv("TWILIO_ACCOUNT_SID")
	auth_token = os.getenv("TWILIO_AUTH_TOKEN")
	from_number = os.getenv("TWILIO_FROM_NUMBER")

	if not account_sid or not auth_token or not from_number:
		return False, "sms_provider_not_configured"

	url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
	try:
		response = requests.post(
			url,
			data={"To": phone, "From": from_number, "Body": message},
			auth=(account_sid, auth_token),
			timeout=12,
		)
	except Exception as exc:
		return False, f"sms_send_error: {exc}"

	if response.status_code in (200, 201):
		return True, "sent"
	detail = response.text.strip().replace("\n", " ")[:300]
	return False, f"sms_send_failed: {response.status_code} {detail}"


def create_booking(
	db: Session,
	name: str,
	gender: str,
	age: int,
	service_name: str,
	phone: str,
	preferred_slot: datetime,
	duration_minutes: int = 60,
	notes: str | None = None,
) -> dict:
	normalized_phone = _normalize_phone(phone)
	if not normalized_phone:
		return {
			"status": "failed",
			"message": "Invalid phone number",
			"notification_sent": False,
			"notification_status": "invalid_phone",
		}

	customer = _find_or_create_customer(db, name=name.strip(), phone=normalized_phone)
	service = _find_or_create_service(db, service_name=service_name)

	slot = _find_next_available_slot(
		db=db,
		preferred_slot=preferred_slot,
		duration_minutes=duration_minutes,
	)
	if slot is None:
		return {
			"status": "failed",
			"message": "No available slot found in the next 12 hours",
			"notification_sent": False,
			"notification_status": "not_sent",
		}

	starts_at, ends_at = slot
	payload = {
		"gender": gender,
		"age": age,
		"notes": notes,
		"service": service.name,
	}
	appointment = Appointment(
		customer_id=customer.id,
		service_id=service.id,
		starts_at=starts_at,
		ends_at=ends_at,
		status="confirmed",
		notes=json.dumps(payload, ensure_ascii=True),
	)
	db.add(appointment)
	db.commit()
	db.refresh(appointment)

	sms_text = (
		f"Hi {customer.name}, your {service.name} booking is confirmed for "
		f"{starts_at.strftime('%Y-%m-%d %I:%M %p')}. Booking ID: {appointment.id}."
	)
	notification_sent, notification_status = _send_booking_sms(normalized_phone, sms_text)

	return {
		"booking_id": appointment.id,
		"status": "confirmed",
		"message": "Booking created successfully",
		"slot_start": starts_at,
		"slot_end": ends_at,
		"notification_sent": notification_sent,
		"notification_status": notification_status,
	}
