import uuid
from datetime import datetime, date
from app.utils.db import db


class Payment(db.Model):
    """Payment record for a candidate."""
    __tablename__ = 'payments'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('candidates.id'), nullable=False)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50))
    payment_date = db.Column(db.Date, nullable=False)
    received_by_user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'))
    is_supplementary = db.Column(db.Boolean, default=False)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    candidate = db.relationship('Candidate', backref=db.backref('payments', lazy='dynamic'))
    received_by = db.relationship('User')

    __table_args__ = (
        db.Index('idx_payments_candidate', 'tenant_id', 'candidate_id'),
        db.Index('idx_payments_date', 'tenant_id', 'payment_date'),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'candidateId': self.candidate_id,
            'tenantId': self.tenant_id,
            'amount': float(self.amount) if self.amount else 0,
            'paymentMethod': self.payment_method,
            'paymentDate': self.payment_date.isoformat() if self.payment_date else None,
            'receivedByUserId': self.received_by_user_id,
            'receivedByUserName': self.received_by.full_name if self.received_by else None,
            'isSupplementary': self.is_supplementary,
            'remarks': self.remarks,
            'createdAt': self.created_at,
        }
