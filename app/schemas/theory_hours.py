from typing import Optional
from app.utils.validation import BaseSchema


class CreateTheorySessionSchema(BaseSchema):
    candidateId: str
    sessionNumber: int
    chapterTopics: str
    dateRealized: Optional[str] = None
    timeFrom: Optional[str] = '16:00'
    timeTo: Optional[str] = '17:30'
    hoursCount: Optional[int] = 2
    isRealized: Optional[bool] = False


class UpdateTheorySessionSchema(BaseSchema):
    chapterTopics: Optional[str] = None
    dateRealized: Optional[str] = None
    timeFrom: Optional[str] = None
    timeTo: Optional[str] = None
    hoursCount: Optional[int] = None
    isRealized: Optional[bool] = None
