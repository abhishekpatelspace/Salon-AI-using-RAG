from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BookingRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    gender: str = Field(min_length=1, max_length=30)
    age: int = Field(ge=1, le=120)
    service: str = Field(min_length=1, max_length=120)
    phone: str = Field(min_length=8, max_length=20)
    preferred_slot: datetime
    duration_minutes: int = Field(default=60, ge=15, le=300)
    notes: Optional[str] = None


class BookingResponse(BaseModel):
    booking_id: Optional[int] = None
    status: str
    message: str
    slot_start: Optional[datetime] = None
    slot_end: Optional[datetime] = None
    notification_sent: bool = False
    notification_status: str = "not_attempted"