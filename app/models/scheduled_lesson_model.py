import uuid
from datetime import datetime, date, time
from app.utils.db import db


class ScheduledLesson(db.Model):
    """Scheduled practical driving lesson."""
    __tablename__ = 'scheduled_lessons'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    instructor_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('instructors.id'), nullable=False)
    candidate_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('candidates.id'), nullable=True)
    title = db.Column(db.String(200))
    vehicle_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('vehicles.id'))
    scheduled_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='scheduled', nullable=False)
    notes = db.Column(db.Text)
    cancelled_reason = db.Column(db.Text)
    practical_session_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('practical_hour_sessions.id', use_alter=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    instructor = db.relationship('Instructor', backref=db.backref('scheduled_lessons', lazy='dynamic'))
    candidate = db.relationship('Candidate', backref=db.backref('scheduled_lessons', lazy='dynamic'))
    vehicle = db.relationship('Vehicle')

    __table_args__ = (
        db.Index('idx_scheduled_lessons_instructor_date', 'tenant_id', 'instructor_id', 'scheduled_date'),
        db.Index('idx_scheduled_lessons_candidate_date', 'tenant_id', 'candidate_id', 'scheduled_date'),
        db.Index('idx_scheduled_lessons_date', 'tenant_id', 'scheduled_date', 'start_time'),
    )

    VALID_STATUSES = ['scheduled', 'completed', 'cancelled', 'no_show']

    def to_dict(self) -> dict:
        return {
            'id': str(self.id),
            'tenantId': str(self.tenant_id),
            'instructorId': str(self.instructor_id),
            'instructorName': self.instructor.full_name if self.instructor else None,
            'candidateId': str(self.candidate_id) if self.candidate_id else None,
            'candidateName': self.candidate.full_name if self.candidate else None,
            'title': self.title,
            'vehicleId': str(self.vehicle_id) if self.vehicle_id else None,
            'vehiclePlate': self.vehicle.plate_number if self.vehicle else None,
            'scheduledDate': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'startTime': self.start_time.strftime('%H:%M') if self.start_time else None,
            'endTime': self.end_time.strftime('%H:%M') if self.end_time else None,
            'status': self.status,
            'notes': self.notes,
            'cancelledReason': self.cancelled_reason,
            'practicalSessionId': str(self.practical_session_id) if self.practical_session_id else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }
