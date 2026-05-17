import uuid
from datetime import datetime
from app.utils.db import db


class ExpenseType(db.Model):
    """Expense type/category (e.g., Fuel, Maintenance, Insurance)."""
    __tablename__ = 'expense_types'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    expenses = db.relationship('Expense', backref='expense_type', lazy='dynamic')

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'name', name='uq_expense_type_tenant_name'),
        db.Index('idx_expense_types_tenant', 'tenant_id'),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'tenantId': self.tenant_id,
            'name': self.name,
            'isActive': self.is_active,
            'createdAt': self.created_at,
        }
