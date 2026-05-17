from typing import Optional, Literal
from app.utils.validation import BaseSchema


class CreateExamSchema(BaseSchema):
    """Schema for creating an exam record."""
    candidateId: str
    examType: Literal['theory', 'practical']
    examDate: str
    score: Optional[int] = None
    result: Optional[Literal['scheduled', 'passed', 'failed', 'cancelled']] = 'scheduled'
    notes: Optional[str] = None
    examinerName: Optional[str] = None
    examLocation: Optional[str] = None


class UpdateExamSchema(BaseSchema):
    """Schema for updating an exam record."""
    examDate: Optional[str] = None
    score: Optional[int] = None
    result: Optional[Literal['scheduled', 'passed', 'failed', 'cancelled']] = None
    notes: Optional[str] = None
    examinerName: Optional[str] = None
    examLocation: Optional[str] = None
