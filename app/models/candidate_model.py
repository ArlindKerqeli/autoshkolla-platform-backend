import uuid
from datetime import datetime, date
from app.utils.db import db


class Candidate(db.Model):
    """Candidate (student) enrolled in a driving school."""
    __tablename__ = 'candidates'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False, index=True)
    code = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    parent_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100), nullable=False)
    personal_number = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(200))

    # Birth location
    birth_country_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('countries.id'))
    birth_municipality_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('municipalities.id'))
    birth_place_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('places.id'))
    birth_municipality_foreign = db.Column(db.String(200))
    birth_place_foreign = db.Column(db.String(200))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(1))  # M or F

    # Residence
    residence_municipality_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('municipalities.id'))
    residence_place_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('places.id'))

    # Category and training
    category_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('categories.id'), nullable=False)
    is_automatic = db.Column(db.Boolean, default=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    amount_paid = db.Column(db.Numeric(10, 2), default=0.00)
    practical_hours = db.Column(db.Integer, default=20)
    theory_hours = db.Column(db.Integer, default=20)
    practical_hours_realized = db.Column(db.Integer, default=0)

    # Registration
    registration_date = db.Column(db.Date, nullable=False)
    protocol_number = db.Column(db.String(50))

    # Documents
    medical_certificate = db.Column(db.Boolean, default=False)
    medical_certificate_number = db.Column(db.String(50))
    medical_certificate_date = db.Column(db.Date)
    verification_flag = db.Column(db.Boolean, default=False)
    red_cross_certificate = db.Column(db.Boolean, default=False)
    id_card_copy = db.Column(db.Boolean, default=False)

    # Assignments
    lecturer_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('instructors.id'))
    instructor_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('instructors.id'))
    vehicle_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('vehicles.id'))

    has_extra_hours = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    comments = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime)

    # Relationships
    category = db.relationship('Category', backref='candidates')
    instructor = db.relationship('Instructor', foreign_keys=[instructor_id], backref=db.backref('candidates', lazy='dynamic'))
    lecturer = db.relationship('Instructor', foreign_keys=[lecturer_id])
    vehicle = db.relationship('Vehicle', backref='candidates')
    birth_country = db.relationship('Country')
    birth_municipality = db.relationship('Municipality', foreign_keys=[birth_municipality_id])
    birth_place = db.relationship('Place', foreign_keys=[birth_place_id])
    residence_municipality = db.relationship('Municipality', foreign_keys=[residence_municipality_id])
    residence_place = db.relationship('Place', foreign_keys=[residence_place_id])

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'code', name='uq_candidates_tenant_code'),
        db.Index('idx_candidates_personal_number', 'tenant_id', 'personal_number'),
        db.Index('idx_candidates_category', 'tenant_id', 'category_id'),
        db.Index('idx_candidates_registration_date', 'tenant_id', 'registration_date'),
        db.Index('idx_candidates_archived', 'tenant_id', 'is_archived'),
        db.Index('idx_candidates_instructor', 'tenant_id', 'instructor_id'),
    )

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    @property
    def debt(self) -> float:
        price = float(self.price) if self.price else 0
        paid = float(self.amount_paid) if self.amount_paid else 0
        return price - paid

    def to_dict(self, summary: bool = False) -> dict:
        """Convert to dict. summary=True for list views with less detail."""
        data = {
            'id': self.id,
            'tenantId': self.tenant_id,
            'firstName': self.first_name,
            'parentName': self.parent_name,
            'lastName': self.last_name,
            'fullName': self.full_name,
            'personalNumber': self.personal_number,
            'phone': self.phone,
            'email': self.email,
            'categoryId': self.category_id,
            'categoryCode': self.category.code if self.category else None,
            'isAutomatic': self.is_automatic,
            'price': float(self.price) if self.price else None,
            'amountPaid': float(self.amount_paid) if self.amount_paid else 0,
            'debt': self.debt,
            'practicalHours': self.practical_hours,
            'theoryHours': self.theory_hours,
            'practicalHoursRealized': self.practical_hours_realized,
            'registrationDate': self.registration_date,
            'protocolNumber': self.protocol_number,
            'instructorId': self.instructor_id,
            'instructorName': self.instructor.full_name if self.instructor else None,
            'lecturerId': self.lecturer_id,
            'lecturerName': self.lecturer.full_name if self.lecturer else None,
            'vehicleId': self.vehicle_id,
            'vehiclePlate': self.vehicle.plate_number if self.vehicle else None,
            'isArchived': self.is_archived,
            'hasExtraHours': self.has_extra_hours,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
        }
        if not summary:
            data.update({
                'dateOfBirth': self.date_of_birth,
                'gender': self.gender,
                'birthCountryId': self.birth_country_id,
                'birthMunicipalityId': self.birth_municipality_id,
                'birthPlaceId': self.birth_place_id,
                'birthMunicipalityForeign': self.birth_municipality_foreign,
                'birthPlaceForeign': self.birth_place_foreign,
                'residenceMunicipalityId': self.residence_municipality_id,
                'residencePlaceId': self.residence_place_id,
                'medicalCertificate': self.medical_certificate,
                'medicalCertificateNumber': self.medical_certificate_number,
                'medicalCertificateDate': self.medical_certificate_date,
                'verificationFlag': self.verification_flag,
                'redCrossCertificate': self.red_cross_certificate,
                'idCardCopy': self.id_card_copy,
                'comments': self.comments,
                'supplementaryRegistrations': [
                    sr.to_dict() for sr in self.supplementary_registrations.all()
                ],
            })
        return data
