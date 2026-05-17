import uuid
from datetime import datetime
from app.utils.db import db


class Tenant(db.Model):
    """
    Tenant model representing a driving school organization.
    Each tenant is isolated in the multi-tenant system.
    """
    __tablename__ = 'tenants'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    nui = db.Column(db.String(50))
    tvsh = db.Column(db.String(50))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    address = db.Column(db.String(300))
    city = db.Column(db.String(100))
    representative = db.Column(db.String(200))
    bank_name = db.Column(db.String(100))
    bank_account = db.Column(db.String(50))
    license_number = db.Column(db.String(50))
    logo_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Tenant {self.name}>'

    def to_dict(self) -> dict:
        """Convert tenant to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'nui': self.nui,
            'tvsh': self.tvsh,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'representative': self.representative,
            'bankName': self.bank_name,
            'bankAccount': self.bank_account,
            'licenseNumber': self.license_number,
            'logoUrl': self.logo_url,
            'isActive': self.is_active,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
        }
