from typing import Optional
from app.utils.validation import BaseSchema


class CreateVerificationSchema(BaseSchema):
    candidateId: str
    categoryId: str
    verificationDate: Optional[str] = None
    theoryHoursStart: Optional[str] = None
    theoryHoursEnd: Optional[str] = None
    practicalHoursStart: Optional[str] = None
    practicalHoursEnd: Optional[str] = None
    sequenceNumber: Optional[str] = None
    lecturerId: Optional[str] = None
    instructorId: Optional[str] = None
    redCrossCert: Optional[bool] = False
    idCardCopy: Optional[bool] = False


class UpdateVerificationSchema(BaseSchema):
    verificationDate: Optional[str] = None
    theoryHoursStart: Optional[str] = None
    theoryHoursEnd: Optional[str] = None
    practicalHoursStart: Optional[str] = None
    practicalHoursEnd: Optional[str] = None
    sequenceNumber: Optional[str] = None
    lecturerId: Optional[str] = None
    instructorId: Optional[str] = None
    redCrossCert: Optional[bool] = None
    idCardCopy: Optional[bool] = None
