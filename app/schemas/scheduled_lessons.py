from typing import Optional
from datetime import date
from app.utils.validation import BaseSchema


class CreateScheduledLessonSchema(BaseSchema):
    instructorId: str
    candidateId: Optional[str] = None
    vehicleId: Optional[str] = None
    scheduledDate: date
    startTime: str  # HH:MM format
    endTime: str    # HH:MM format
    title: Optional[str] = None
    notes: Optional[str] = None


class UpdateScheduledLessonSchema(BaseSchema):
    candidateId: Optional[str] = None
    vehicleId: Optional[str] = None
    scheduledDate: Optional[date] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    title: Optional[str] = None
    notes: Optional[str] = None


class CreatePersonalEventSchema(BaseSchema):
    title: str
    scheduledDate: date
    startTime: str  # HH:MM format
    endTime: str    # HH:MM format
    notes: Optional[str] = None
    candidateId: Optional[str] = None
