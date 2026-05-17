import uuid
from datetime import datetime, date
from app.utils.db import db


class Expense(db.Model):
    """Vehicle maintenance and operational expense record."""
    __tablename__ = 'expenses'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    vehicle_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('vehicles.id'))
    expense_type_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('expense_types.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    vehicle = db.relationship('Vehicle', backref=db.backref('expenses', lazy='dynamic'))

    __table_args__ = (
        db.Index('idx_expenses_date', 'tenant_id', 'date'),
        db.Index('idx_expenses_vehicle', 'tenant_id', 'vehicle_id'),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'tenantId': self.tenant_id,
            'vehicleId': self.vehicle_id,
            'vehiclePlate': self.vehicle.plate_number if self.vehicle else None,
            'expenseTypeId': self.expense_type_id,
            'expenseTypeName': self.expense_type.name if self.expense_type else None,
            'date': self.date.isoformat() if self.date else None,
            'amount': float(self.amount) if self.amount else 0,
            'description': self.description,
            'createdAt': self.created_at,
        }
