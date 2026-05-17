from typing import Optional
from app.utils.validation import BaseSchema


class CreatePracticalSessionSchema(BaseSchema):
    candidateId: str
    instructorId: Optional[str] = None
    dateRealized: str
    timeRealized: str
    hoursCount: Optional[int] = 1
    pricePerHour: Optional[float] = 0.00
    chapterTopics: Optional[str] = None
    remarks: Optional[str] = None
    isPaid: Optional[bool] = False


class UpdatePracticalSessionSchema(BaseSchema):
    instructorId: Optional[str] = None
    dateRealized: Optional[str] = None
    timeRealized: Optional[str] = None
    hoursCount: Optional[int] = None
    pricePerHour: Optional[float] = None
    chapterTopics: Optional[str] = None
    remarks: Optional[str] = None
    isPaid: Optional[bool] = None
