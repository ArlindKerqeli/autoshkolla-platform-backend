import uuid
from datetime import datetime
from app.utils.db import db


class Category(db.Model):
    """Driving license category (B, C, CE, D, etc.) per tenant."""
    __tablename__ = 'categories'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False, index=True)
    code = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(300))
    verification_text = db.Column(db.Text)
    verification_code = db.Column(db.String(50))
    theory_hours = db.Column(db.Integer, default=20)
    practical_hours = db.Column(db.Integer, default=20)
    price = db.Column(db.Numeric(10, 2), default=350.00)
    contract_price = db.Column(db.Numeric(10, 2))
    is_licensed = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'code', name='uq_categories_tenant_code'),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'tenantId': self.tenant_id,
            'code': self.code,
            'description': self.description,
            'verificationText': self.verification_text,
            'verificationCode': self.verification_code,
            'theoryHours': self.theory_hours,
            'practicalHours': self.practical_hours,
            'price': float(self.price) if self.price else None,
            'contractPrice': float(self.contract_price) if self.contract_price else None,
            'isLicensed': self.is_licensed,
            'isActive': self.is_active,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
        }
