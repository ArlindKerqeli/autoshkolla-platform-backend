import re
import uuid
from datetime import datetime
from app.utils.db import db
from app.models.candidate_model import Candidate
from app.middleware.error_handler import ValidationError, NotFound


def _clean_uuid(value) -> str | None:
    """Convert empty strings to None for optional UUID fields."""
    if not value or (isinstance(value, str) and value.strip() == ''):
        return None
    return value


class CandidateService:
    """Business logic for candidate management."""

    def generate_code(self, tenant_id: str) -> str:
        """Generate next candidate code for tenant. Format: 10000XXXXX"""
        last = Candidate.query.filter_by(tenant_id=tenant_id)\
            .order_by(Candidate.code.desc()).first()
        if last and last.code.isdigit():
            return str(int(last.code) + 1)
        return '1000000001'

    def generate_protocol_number(self, tenant_id: str) -> str:
        """Generate next protocol number for tenant. Format: {number}/{year}"""
        current_year = datetime.utcnow().year

        # Use SQL LIKE to only fetch candidates with current year protocol numbers
        pattern = f'%/{current_year}'
        candidates = Candidate.query.filter_by(
            tenant_id=tenant_id
        ).filter(
            Candidate.protocol_number.like(pattern)
        ).all()

        max_num = 0
        for c in candidates:
            pn = c.protocol_number.strip()
            match = re.match(r'^(\d+)/' + str(current_year) + r'$', pn)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num

        return f'{max_num + 1}/{current_year}'

    def create_candidate(self, tenant_id: str, data: dict) -> Candidate:
        """Create a new candidate."""
        # Generate code
        code = self.generate_code(tenant_id)

        # Validate gender
        if data.get('gender') and data['gender'] not in ('M', 'F'):
            raise ValidationError("Gender must be 'M' or 'F'")

        candidate = Candidate(
            tenant_id=tenant_id,
            code=code,
            first_name=data['firstName'],
            parent_name=data.get('parentName'),
            last_name=data['lastName'],
            personal_number=data['personalNumber'],
            phone=data.get('phone'),
            email=data.get('email'),
            birth_country_id=_clean_uuid(data.get('birthCountryId')),
            birth_municipality_id=_clean_uuid(data.get('birthMunicipalityId')),
            birth_place_id=_clean_uuid(data.get('birthPlaceId')),
            birth_municipality_foreign=data.get('birthMunicipalityForeign'),
            birth_place_foreign=data.get('birthPlaceForeign'),
            date_of_birth=data.get('dateOfBirth'),
            gender=data.get('gender'),
            residence_municipality_id=_clean_uuid(data.get('residenceMunicipalityId')),
            residence_place_id=_clean_uuid(data.get('residencePlaceId')),
            category_id=data['categoryId'],
            is_automatic=data.get('isAutomatic', False),
            price=data['price'],
            practical_hours=data.get('practicalHours', 20),
            theory_hours=data.get('theoryHours', 20),
            registration_date=data['registrationDate'],
            protocol_number=data.get('protocolNumber'),
            medical_certificate=data.get('medicalCertificate', False),
            medical_certificate_number=data.get('medicalCertificateNumber'),
            medical_certificate_date=data.get('medicalCertificateDate'),
            verification_flag=data.get('verificationFlag', False),
            red_cross_certificate=data.get('redCrossCertificate', False),
            id_card_copy=data.get('idCardCopy', False),
            lecturer_id=_clean_uuid(data.get('lecturerId')),
            instructor_id=_clean_uuid(data.get('instructorId')),
            vehicle_id=_clean_uuid(data.get('vehicleId')),
            comments=data.get('comments'),
        )

        db.session.add(candidate)

        # Auto-create instructor payment record if instructor assigned
        if candidate.instructor_id:
            self._create_instructor_payment(tenant_id, candidate)

        db.session.commit()
        return candidate

    def update_candidate(self, tenant_id: str, candidate_id: str, data: dict) -> Candidate:
        """Update an existing candidate."""
        candidate = Candidate.query.filter_by(
            id=candidate_id, tenant_id=tenant_id, deleted_at=None
        ).first()
        if not candidate:
            raise NotFound('Candidate not found')

        old_instructor_id = candidate.instructor_id

        # Map schema fields to model fields
        field_map = {
            'firstName': 'first_name', 'parentName': 'parent_name',
            'lastName': 'last_name', 'personalNumber': 'personal_number',
            'phone': 'phone', 'email': 'email',
            'birthCountryId': 'birth_country_id', 'birthMunicipalityId': 'birth_municipality_id',
            'birthPlaceId': 'birth_place_id', 'birthMunicipalityForeign': 'birth_municipality_foreign',
            'birthPlaceForeign': 'birth_place_foreign', 'dateOfBirth': 'date_of_birth',
            'gender': 'gender', 'residenceMunicipalityId': 'residence_municipality_id',
            'residencePlaceId': 'residence_place_id', 'categoryId': 'category_id',
            'isAutomatic': 'is_automatic', 'price': 'price',
            'practicalHours': 'practical_hours', 'theoryHours': 'theory_hours',
            'protocolNumber': 'protocol_number',
            'medicalCertificate': 'medical_certificate',
            'medicalCertificateNumber': 'medical_certificate_number',
            'medicalCertificateDate': 'medical_certificate_date',
            'verificationFlag': 'verification_flag',
            'redCrossCertificate': 'red_cross_certificate',
            'idCardCopy': 'id_card_copy',
            'lecturerId': 'lecturer_id', 'instructorId': 'instructor_id',
            'vehicleId': 'vehicle_id', 'comments': 'comments',
        }
        uuid_fields = {
            'birthCountryId', 'birthMunicipalityId', 'birthPlaceId',
            'residenceMunicipalityId', 'residencePlaceId', 'categoryId',
            'lecturerId', 'instructorId', 'vehicleId',
        }
        for schema_key, model_key in field_map.items():
            if schema_key in data:
                value = data[schema_key]
                if schema_key in uuid_fields:
                    value = _clean_uuid(value)
                setattr(candidate, model_key, value)

        # If instructor changed, create new instructor payment
        new_instructor_id = candidate.instructor_id
        if new_instructor_id and new_instructor_id != old_instructor_id:
            self._create_instructor_payment(tenant_id, candidate)

        db.session.commit()
        return candidate

    def soft_delete(self, tenant_id: str, candidate_id: str) -> None:
        """Soft-delete a candidate."""
        candidate = Candidate.query.filter_by(
            id=candidate_id, tenant_id=tenant_id, deleted_at=None
        ).first()
        if not candidate:
            raise NotFound('Candidate not found')
        candidate.deleted_at = datetime.utcnow()
        db.session.commit()

    def archive(self, tenant_id: str, candidate_id: str) -> Candidate:
        """Move candidate to archive."""
        candidate = Candidate.query.filter_by(
            id=candidate_id, tenant_id=tenant_id, deleted_at=None
        ).first()
        if not candidate:
            raise NotFound('Candidate not found')
        candidate.is_archived = True
        db.session.commit()
        return candidate

    def bulk_archive(self, tenant_id: str, candidate_ids: list[str]) -> int:
        """Archive multiple candidates at once. Returns count of affected rows."""
        count = Candidate.query.filter(
            Candidate.id.in_(candidate_ids),
            Candidate.tenant_id == tenant_id,
            Candidate.deleted_at.is_(None),
            Candidate.is_archived == False,
        ).update({'is_archived': True, 'updated_at': datetime.utcnow()}, synchronize_session='fetch')
        db.session.commit()
        return count

    def bulk_unarchive(self, tenant_id: str, candidate_ids: list[str]) -> int:
        """Unarchive multiple candidates at once. Returns count of affected rows."""
        count = Candidate.query.filter(
            Candidate.id.in_(candidate_ids),
            Candidate.tenant_id == tenant_id,
            Candidate.deleted_at.is_(None),
            Candidate.is_archived == True,
        ).update({'is_archived': False, 'updated_at': datetime.utcnow()}, synchronize_session='fetch')
        db.session.commit()
        return count

    def _create_instructor_payment(self, tenant_id: str, candidate: Candidate) -> None:
        """Auto-create instructor payment when candidate is assigned to instructor."""
        from app.models.instructor_model import Instructor
        instructor = Instructor.query.get(candidate.instructor_id)
        if not instructor:
            return
        # Check if payment record already exists for this pair
        from app.models.instructor_payment_model import InstructorPayment
        existing = InstructorPayment.query.filter_by(
            tenant_id=tenant_id,
            instructor_id=str(instructor.id),
            candidate_id=str(candidate.id)
        ).first()
        if not existing:
            payment = InstructorPayment(
                tenant_id=tenant_id,
                instructor_id=instructor.id,
                candidate_id=candidate.id,
                amount=float(instructor.cost_per_candidate) if instructor.cost_per_candidate else 65.00,
            )
            db.session.add(payment)
