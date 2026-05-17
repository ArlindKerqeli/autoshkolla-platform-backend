from typing import Optional
from app.utils.validation import BaseSchema


class CreateExpenseTypeSchema(BaseSchema):
    name: str
    isActive: Optional[bool] = True


class UpdateExpenseTypeSchema(BaseSchema):
    name: Optional[str] = None
    isActive: Optional[bool] = None


class CreateExpenseSchema(BaseSchema):
    vehicleId: Optional[str] = None
    expenseTypeId: str
    date: str
    amount: float
    description: Optional[str] = None


class UpdateExpenseSchema(BaseSchema):
    vehicleId: Optional[str] = None
    expenseTypeId: Optional[str] = None
    date: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None
