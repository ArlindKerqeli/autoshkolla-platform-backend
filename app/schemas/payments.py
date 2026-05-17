from typing import Optional
from app.utils.validation import BaseSchema


class CreatePaymentSchema(BaseSchema):
    candidateId: str
    amount: float
    paymentMethod: Optional[str] = None
    paymentDate: str
    isSupplementary: Optional[bool] = False
    remarks: Optional[str] = None


class RecordPaymentSchema(BaseSchema):
    amount: float
    paymentMethod: Optional[str] = None
    paymentDate: str
    remarks: Optional[str] = None
