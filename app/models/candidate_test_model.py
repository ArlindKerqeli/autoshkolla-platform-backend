import uuid
from datetime import datetime, date
from app.utils.db import db


class CandidateTest(db.Model):
    """Test result record for a candidate (theory or practical exam)."""
    __tablename__ = 'candidate_tests'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('candidates.id'), nullable=False)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    test_number = db.Column(db.Integer)
    score = db.Column(db.Integer)
    passing_score = db.Column(db.Integer, default=85)
    date_taken = db.Column(db.Date)
    is_passed = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    candidate = db.relationship('Candidate', backref=db.backref('tests', lazy='dynamic'))

    __table_args__ = (
        db.Index('idx_candidate_tests_candidate', 'tenant_id', 'candidate_id'),
        db.Index('idx_candidate_tests_date', 'tenant_id', 'date_taken'),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'candidateId': self.candidate_id,
            'tenantId': self.tenant_id,
            'testNumber': self.test_number,
            'score': self.score,
            'passingScore': self.passing_score,
            'dateTaken': self.date_taken.isoformat() if self.date_taken else None,
            'isPassed': self.is_passed,
            'createdAt': self.created_at,
        }
