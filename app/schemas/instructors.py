from typing import Optional
from datetime import date
from decimal import Decimal
from app.utils.validation import BaseSchema


class CreateInstructorSchema(BaseSchema):
    code: str
    firstName: str
    lastName: str
    personalNumber: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    position: str = 'instructor'
    licenseInfo: Optional[str] = None
    licenseExpiry: Optional[date] = None
    costPerCandidate: Decimal = Decimal('65.00')


class UpdateInstructorSchema(BaseSchema):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    personalNumber: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    licenseInfo: Optional[str] = None
    licenseExpiry: Optional[date] = None
    costPerCandidate: Optional[Decimal] = None
    isActive: Optional[bool] = None
