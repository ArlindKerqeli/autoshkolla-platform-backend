import uuid
from datetime import datetime, date, time
from app.utils.db import db


class PracticalHourSession(db.Model):
    """Practical driving hour session for a candidate with an instructor."""
    __tablename__ = 'practical_hour_sessions'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('candidates.id'), nullable=False)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    instructor_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('instructors.id'))
    date_realized = db.Column(db.Date, nullable=False)
    time_realized = db.Column(db.Time, nullable=False)
    hours_count = db.Column(db.Integer, default=1)
    price_per_hour = db.Column(db.Numeric(10, 2), default=0.00)
    chapter_topics = db.Column(db.String(200), nullable=True)
    remarks = db.Column(db.Text)
    is_paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    candidate = db.relationship('Candidate', backref=db.backref('practical_sessions', lazy='dynamic'))
    instructor = db.relationship('Instructor', backref=db.backref('practical_sessions', lazy='dynamic'))

    __table_args__ = (
        db.Index('idx_practical_sessions_candidate', 'tenant_id', 'candidate_id'),
        db.Index('idx_practical_sessions_instructor', 'tenant_id', 'instructor_id'),
        db.Index('idx_practical_sessions_date', 'tenant_id', 'date_realized'),
    )

    @property
    def total_price(self) -> float:
        hours = float(self.hours_count) if self.hours_count else 0
        price = float(self.price_per_hour) if self.price_per_hour else 0
        return hours * price

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'candidateId': self.candidate_id,
            'tenantId': self.tenant_id,
            'instructorId': self.instructor_id,
            'instructorName': self.instructor.full_name if self.instructor else None,
            'dateRealized': self.date_realized.isoformat() if self.date_realized else None,
            'timeRealized': self.time_realized.strftime('%H:%M') if self.time_realized else None,
            'hoursCount': self.hours_count,
            'pricePerHour': float(self.price_per_hour) if self.price_per_hour else 0,
            'totalPrice': self.total_price,
            'chapterTopics': self.chapter_topics,
            'remarks': self.remarks,
            'isPaid': self.is_paid,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
        }
