import uuid
from datetime import datetime, time
from app.utils.db import db


class LessonChapter(db.Model):
    """Predefined lesson chapter template per category (theory or practical)."""
    __tablename__ = 'lesson_chapters'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    category_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('categories.id'), nullable=False)
    chapter_type = db.Column(db.String(10), nullable=False)
    session_number = db.Column(db.Integer, nullable=False)
    chapter_topics = db.Column(db.String(200), nullable=False)
    time_from = db.Column(db.Time, nullable=True)
    time_to = db.Column(db.Time, nullable=True)
    hours_count = db.Column(db.Integer, default=2, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    category = db.relationship('Category', backref=db.backref('lesson_chapters', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint(
            'tenant_id', 'category_id', 'chapter_type', 'session_number',
            name='uq_lesson_chapter_tenant_cat_type_num'
        ),
        db.CheckConstraint("chapter_type IN ('theory', 'practical')", name='ck_lesson_chapter_type'),
        db.Index('idx_lesson_chapters_tenant_cat_type', 'tenant_id', 'category_id', 'chapter_type'),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'tenantId': self.tenant_id,
            'categoryId': self.category_id,
            'categoryCode': self.category.code if self.category else None,
            'chapterType': self.chapter_type,
            'sessionNumber': self.session_number,
            'chapterTopics': self.chapter_topics,
            'timeFrom': self.time_from.strftime('%H:%M') if self.time_from else None,
            'timeTo': self.time_to.strftime('%H:%M') if self.time_to else None,
            'hoursCount': self.hours_count,
            'isActive': self.is_active,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
        }
