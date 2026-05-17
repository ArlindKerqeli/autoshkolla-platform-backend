import uuid
from datetime import datetime
from app.utils.db import db


class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(10), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    municipalities = db.relationship('Municipality', backref='country', lazy='dynamic')

    def to_dict(self):
        return {'id': str(self.id), 'name': self.name, 'code': self.code}
