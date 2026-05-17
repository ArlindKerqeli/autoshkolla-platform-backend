import uuid
from datetime import datetime
from app.utils.db import db


class Place(db.Model):
    __tablename__ = 'places'
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    municipality_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('municipalities.id'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {'id': str(self.id), 'municipalityId': str(self.municipality_id), 'name': self.name, 'code': self.code}
