import uuid
from datetime import datetime, date
from app.utils.db import db


class SupplementaryRegistration(db.Model):
    """Additional registration for a candidate in a new category."""
    __tablename__ = 'supplementary_registrations'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('candidates.id'), nullable=False)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    category_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('categories.id'), nullable=False)
    is_automatic = db.Column(db.Boolean, default=False)
    price = db.Column(db.Numeric(10, 2))
    practical_hours = db.Column(db.Integer)
    theory_hours = db.Column(db.Integer)
    registration_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    candidate = db.relationship('Candidate', backref=db.backref('supplementary_registrations', lazy='dynamic'))
    category = db.relationship('Category')

    __table_args__ = (
        db.Index('idx_supplementary_registrations_candidate', 'tenant_id', 'candidate_id'),
        db.Index('idx_supplementary_registrations_date', 'tenant_id', 'registration_date'),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'candidateId': self.candidate_id,
            'tenantId': self.tenant_id,
            'categoryId': self.category_id,
            'categoryCode': self.category.code if self.category else None,
            'isAutomatic': self.is_automatic,
            'price': float(self.price) if self.price else None,
            'practicalHours': self.practical_hours,
            'theoryHours': self.theory_hours,
            'registrationDate': self.registration_date.isoformat() if self.registration_date else None,
            'createdAt': self.created_at,
        }
