from typing import Optional
from app.utils.validation import BaseSchema


class CreateTenantSchema(BaseSchema):
    """Schema for creating a new tenant."""
    name: str
    slug: str
    contactEmail: Optional[str] = None
    contactPhone: Optional[str] = None
    address: Optional[str] = None


class UpdateTenantSchema(BaseSchema):
    """Schema for updating a tenant."""
    name: Optional[str] = None
    contactEmail: Optional[str] = None
    contactPhone: Optional[str] = None
    address: Optional[str] = None
    isActive: Optional[bool] = None


class CreateTenantUserSchema(BaseSchema):
    """Schema for creating an administrator user for a tenant."""
    email: str
    password: str
    fullName: str
    role: str  # 'administrator'


class UpdateTenantUserSchema(BaseSchema):
    """Schema for updating a user within a tenant."""
    fullName: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    isActive: Optional[bool] = None
    password: Optional[str] = None


class ImpersonateSchema(BaseSchema):
    """Schema for starting user impersonation."""
    userId: str
