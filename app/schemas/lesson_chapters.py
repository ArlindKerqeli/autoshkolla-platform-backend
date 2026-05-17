from typing import Optional
from app.utils.validation import BaseSchema


class CreateLessonChapterSchema(BaseSchema):
    categoryId: str
    chapterType: str
    chapterTopics: str
    timeFrom: Optional[str] = None
    timeTo: Optional[str] = None
    hoursCount: Optional[int] = 2
    isActive: Optional[bool] = True


class UpdateLessonChapterSchema(BaseSchema):
    chapterTopics: Optional[str] = None
    timeFrom: Optional[str] = None
    timeTo: Optional[str] = None
    hoursCount: Optional[int] = None
    isActive: Optional[bool] = None
