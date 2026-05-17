from typing import Optional
from app.utils.validation import BaseSchema


class CreateUserSchema(BaseSchema):
    email: str
    password: str
    fullName: str
    role: str  # 'administrator', 'instructor', 'lecturer'


class UpdateUserSchema(BaseSchema):
    email: Optional[str] = None
    fullName: Optional[str] = None
    role: Optional[str] = None
    isActive: Optional[bool] = None


class ChangePasswordSchema(BaseSchema):
    password: str
