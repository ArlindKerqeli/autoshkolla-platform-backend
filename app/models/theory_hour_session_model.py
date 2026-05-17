import uuid
from datetime import datetime, date, time
from app.utils.db import db


class TheoryHourSession(db.Model):
    """Theory driving hour session for a candidate."""
    __tablename__ = 'theory_hour_sessions'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('candidates.id'), nullable=False)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    session_number = db.Column(db.Integer, nullable=False)
    chapter_topics = db.Column(db.String(100), nullable=False)
    date_realized = db.Column(db.Date)
    time_from = db.Column(db.Time, default=time(16, 0))
    time_to = db.Column(db.Time, default=time(17, 30))
    hours_count = db.Column(db.Integer, default=2)
    is_realized = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    candidate = db.relationship('Candidate', backref=db.backref('theory_sessions', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('candidate_id', 'session_number', name='uq_theory_session_candidate_number'),
        db.Index('idx_theory_sessions_candidate', 'tenant_id', 'candidate_id'),
        db.Index('idx_theory_sessions_date', 'tenant_id', 'date_realized'),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'candidateId': self.candidate_id,
            'tenantId': self.tenant_id,
            'sessionNumber': self.session_number,
            'chapterTopics': self.chapter_topics,
            'dateRealized': self.date_realized.isoformat() if self.date_realized else None,
            'timeFrom': self.time_from.strftime('%H:%M') if self.time_from else None,
            'timeTo': self.time_to.strftime('%H:%M') if self.time_to else None,
            'hoursCount': self.hours_count,
            'isRealized': self.is_realized,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
        }
