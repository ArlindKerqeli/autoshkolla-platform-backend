from typing import Optional
from decimal import Decimal
from app.utils.validation import BaseSchema


class CreateCategorySchema(BaseSchema):
    code: str
    description: Optional[str] = None
    verificationText: Optional[str] = None
    verificationCode: Optional[str] = None
    theoryHours: int = 20
    practicalHours: int = 20
    price: Decimal = Decimal('350.00')
    contractPrice: Optional[Decimal] = None
    isLicensed: bool = False


class UpdateCategorySchema(BaseSchema):
    code: Optional[str] = None
    description: Optional[str] = None
    verificationText: Optional[str] = None
    verificationCode: Optional[str] = None
    theoryHours: Optional[int] = None
    practicalHours: Optional[int] = None
    price: Optional[Decimal] = None
    contractPrice: Optional[Decimal] = None
    isLicensed: Optional[bool] = None
    isActive: Optional[bool] = None
