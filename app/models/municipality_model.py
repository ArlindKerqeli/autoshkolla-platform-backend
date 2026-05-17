import uuid
from datetime import datetime
from app.utils.db import db


class Municipality(db.Model):
    __tablename__ = 'municipalities'
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    country_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('countries.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.Integer, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    places = db.relationship('Place', backref='municipality', lazy='dynamic')

    def to_dict(self):
        return {'id': str(self.id), 'countryId': str(self.country_id), 'name': self.name, 'code': self.code}
