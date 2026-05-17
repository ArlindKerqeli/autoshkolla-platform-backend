import uuid
from datetime import datetime, date
from app.utils.db import db


class Instructor(db.Model):
    """Instructor/Lecturer for a driving school tenant."""
    __tablename__ = 'instructors'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False, index=True)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True, unique=True, index=True)
    code = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    personal_number = db.Column(db.String(20))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    position = db.Column(db.String(20), nullable=False, default='instructor')
    hours_realized = db.Column(db.Integer, default=0)
    license_info = db.Column(db.String(200))
    license_expiry = db.Column(db.Date, nullable=True)
    cost_per_candidate = db.Column(db.Numeric(10, 2), default=65.00)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref=db.backref('instructor', uselist=False))

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'code', name='uq_instructors_tenant_code'),
    )

    VALID_POSITIONS = ['instructor', 'lecturer', 'both']

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def to_dict(self, include_user: bool = False) -> dict:
        data = {
            'id': self.id,
            'tenantId': self.tenant_id,
            'userId': self.user_id,
            'code': self.code,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'fullName': self.full_name,
            'personalNumber': self.personal_number,
            'email': self.email,
            'phone': self.phone,
            'position': self.position,
            'hoursRealized': self.hours_realized,
            'licenseInfo': self.license_info,
            'licenseExpiry': self.license_expiry.isoformat() if self.license_expiry else None,
            'costPerCandidate': float(self.cost_per_candidate) if self.cost_per_candidate else 65.00,
            'isActive': self.is_active,
            'hasLogin': self.user_id is not None,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
        }
        return data
