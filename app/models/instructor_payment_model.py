import uuid
from datetime import datetime
from app.utils.db import db


class InstructorPayment(db.Model):
    """Tracks what each instructor owes per assigned candidate."""
    __tablename__ = 'instructor_payments'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    instructor_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('instructors.id'), nullable=False)
    candidate_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('candidates.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False, default=65.00)
    amount_paid = db.Column(db.Numeric(10, 2), default=0.00)
    payment_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))
    status = db.Column(db.String(20), default='unpaid', nullable=False)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    instructor = db.relationship('Instructor', backref=db.backref('payments_owed', lazy='dynamic'))
    candidate = db.relationship('Candidate', backref=db.backref('instructor_payment', uselist=False))

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'instructor_id', 'candidate_id', name='uq_instructor_payment_candidate'),
        db.Index('idx_instructor_payments_tenant', 'tenant_id', 'instructor_id'),
        db.Index('idx_instructor_payments_status', 'tenant_id', 'status'),
    )

    VALID_STATUSES = ['unpaid', 'partial', 'paid']

    @property
    def outstanding(self) -> float:
        amt = float(self.amount) if self.amount else 0
        paid = float(self.amount_paid) if self.amount_paid else 0
        return amt - paid

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'tenantId': self.tenant_id,
            'instructorId': self.instructor_id,
            'candidateId': self.candidate_id,
            'candidateName': self.candidate.full_name if self.candidate else None,
            'amount': float(self.amount) if self.amount else 0,
            'amountPaid': float(self.amount_paid) if self.amount_paid else 0,
            'outstanding': self.outstanding,
            'paymentDate': self.payment_date,
            'paymentMethod': self.payment_method,
            'status': self.status,
            'remarks': self.remarks,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
        }
