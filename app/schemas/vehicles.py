from typing import Optional
from datetime import date
from app.utils.validation import BaseSchema


class CreateVehicleSchema(BaseSchema):
    make: str
    model: Optional[str] = None
    chassisNumber: Optional[str] = None
    plateNumber: str
    registrationDate: Optional[date] = None
    registrationExpiry: Optional[date] = None
    technicalControlDate: Optional[date] = None
    insuranceExpiry: Optional[date] = None
    instructorId: Optional[str] = None


class UpdateVehicleSchema(BaseSchema):
    make: Optional[str] = None
    model: Optional[str] = None
    chassisNumber: Optional[str] = None
    plateNumber: Optional[str] = None
    registrationDate: Optional[date] = None
    registrationExpiry: Optional[date] = None
    technicalControlDate: Optional[date] = None
    insuranceExpiry: Optional[date] = None
    instructorId: Optional[str] = None
    isActive: Optional[bool] = None
