import uuid
from datetime import datetime, date
from app.utils.db import db


class Verification(db.Model):
    """Verification/certification record for a candidate completing training."""
    __tablename__ = 'verifications'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('candidates.id'), nullable=False)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    category_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('categories.id'), nullable=False)
    verification_date = db.Column(db.Date)
    theory_hours_start = db.Column(db.Date)
    theory_hours_end = db.Column(db.Date)
    practical_hours_start = db.Column(db.Date)
    practical_hours_end = db.Column(db.Date)
    sequence_number = db.Column(db.String(50))
    lecturer_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('instructors.id'))
    instructor_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('instructors.id'))
    red_cross_cert = db.Column(db.Boolean, default=False)
    id_card_copy = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    candidate = db.relationship('Candidate', backref=db.backref('verifications', lazy='dynamic'))
    category = db.relationship('Category')
    lecturer = db.relationship('Instructor', foreign_keys=[lecturer_id])
    instructor = db.relationship('Instructor', foreign_keys=[instructor_id])

    __table_args__ = (
        db.Index('idx_verifications_candidate', 'tenant_id', 'candidate_id'),
        db.Index('idx_verifications_category', 'tenant_id', 'category_id'),
        db.Index('idx_verifications_date', 'tenant_id', 'verification_date'),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'candidateId': self.candidate_id,
            'tenantId': self.tenant_id,
            'categoryId': self.category_id,
            'categoryCode': self.category.code if self.category else None,
            'verificationDate': self.verification_date.isoformat() if self.verification_date else None,
            'theoryHoursStart': self.theory_hours_start.isoformat() if self.theory_hours_start else None,
            'theoryHoursEnd': self.theory_hours_end.isoformat() if self.theory_hours_end else None,
            'practicalHoursStart': self.practical_hours_start.isoformat() if self.practical_hours_start else None,
            'practicalHoursEnd': self.practical_hours_end.isoformat() if self.practical_hours_end else None,
            'sequenceNumber': self.sequence_number,
            'lecturerId': self.lecturer_id,
            'lecturerName': self.lecturer.full_name if self.lecturer else None,
            'instructorId': self.instructor_id,
            'instructorName': self.instructor.full_name if self.instructor else None,
            'redCrossCert': self.red_cross_cert,
            'idCardCopy': self.id_card_copy,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
        }
