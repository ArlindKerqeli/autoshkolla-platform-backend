import uuid
from datetime import datetime, date
from app.utils.db import db


class Exam(db.Model):
    """Official exam record for a candidate (theory or practical)."""
    __tablename__ = 'exams'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    candidate_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('candidates.id'), nullable=False)
    exam_type = db.Column(db.String(20), nullable=False)  # 'theory' or 'practical'
    exam_date = db.Column(db.Date, nullable=False)
    score = db.Column(db.Integer, nullable=True)
    result = db.Column(db.String(20), nullable=False, default='scheduled')  # scheduled/passed/failed/cancelled
    attempt_number = db.Column(db.Integer, nullable=False, default=1)
    notes = db.Column(db.Text, nullable=True)
    examiner_name = db.Column(db.String(200), nullable=True)
    exam_location = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    candidate = db.relationship('Candidate', backref=db.backref('exams', lazy='dynamic'))

    __table_args__ = (
        db.Index('idx_exams_tenant_candidate', 'tenant_id', 'candidate_id'),
        db.Index('idx_exams_tenant_date', 'tenant_id', 'exam_date'),
        db.Index('idx_exams_tenant_type_result', 'tenant_id', 'exam_type', 'result'),
    )

    def to_dict(self) -> dict:
        d = {
            'id': self.id,
            'tenantId': self.tenant_id,
            'candidateId': self.candidate_id,
            'examType': self.exam_type,
            'examDate': self.exam_date.isoformat() if self.exam_date else None,
            'score': self.score,
            'result': self.result,
            'attemptNumber': self.attempt_number,
            'notes': self.notes,
            'examinerName': self.examiner_name,
            'examLocation': self.exam_location,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
        }
        if self.candidate:
            d['candidateName'] = f"{self.candidate.first_name} {self.candidate.last_name}"
            d['candidateCode'] = self.candidate.code
        return d
