import uuid
from datetime import datetime, date
from app.utils.db import db


class Vehicle(db.Model):
    """Vehicle assigned to a driving school tenant."""
    __tablename__ = 'vehicles'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False, index=True)
    make = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100))
    chassis_number = db.Column(db.String(50))
    plate_number = db.Column(db.String(20), nullable=False)
    registration_date = db.Column(db.Date)
    registration_expiry = db.Column(db.Date)
    technical_control_date = db.Column(db.Date)
    insurance_expiry = db.Column(db.Date, nullable=True)
    instructor_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('instructors.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    instructor = db.relationship('Instructor', backref=db.backref('vehicles', lazy='dynamic'))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'tenantId': self.tenant_id,
            'make': self.make,
            'model': self.model,
            'chassisNumber': self.chassis_number,
            'plateNumber': self.plate_number,
            'registrationDate': self.registration_date,
            'registrationExpiry': self.registration_expiry,
            'technicalControlDate': self.technical_control_date,
            'insuranceExpiry': self.insurance_expiry.isoformat() if self.insurance_expiry else None,
            'instructorId': self.instructor_id,
            'instructorName': self.instructor.full_name if self.instructor else None,
            'isActive': self.is_active,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
        }
