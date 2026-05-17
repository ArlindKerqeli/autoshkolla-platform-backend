from app.utils.db import db
from app.models.instructor_model import Instructor
from app.models.user_model import User
from app.middleware.error_handler import ValidationError, NotFound, Forbidden


class InstructorService:
    """Business logic for instructor management."""

    def create_instructor(self, tenant_id: str, data: dict) -> Instructor:
        """Create instructor. If email+password provided, auto-create user account."""
        # Validate position
        if data.get('position') and data['position'] not in Instructor.VALID_POSITIONS:
            raise ValidationError(f"Invalid position. Must be one of: {', '.join(Instructor.VALID_POSITIONS)}")

        # Check unique code
        existing = Instructor.query.filter_by(tenant_id=tenant_id, code=data['code']).first()
        if existing:
            raise ValidationError(f"Instructor with code '{data['code']}' already exists")

        instructor = Instructor(
            tenant_id=tenant_id,
            code=data['code'],
            first_name=data['firstName'],
            last_name=data['lastName'],
            personal_number=data.get('personalNumber'),
            email=data.get('email'),
            phone=data.get('phone'),
            position=data.get('position', 'instructor'),
            license_info=data.get('licenseInfo'),
            license_expiry=data.get('licenseExpiry'),
            cost_per_candidate=data.get('costPerCandidate', 65.00),
        )

        # If email and password provided, create a user account for login
        email = data.get('email')
        password = data.get('password')
        if email and password:
            # Check if email already used as username
            existing_user = User.query.filter_by(tenant_id=tenant_id, username=email).first()
            if existing_user:
                raise ValidationError(f"A user with email '{email}' already exists")

            user = User(
                tenant_id=tenant_id,
                username=email,
                full_name=f"{data['firstName']} {data['lastName']}",
                personal_number=data.get('personalNumber'),
                email=email,
                role='instructor',
            )
            user.set_password(password)
            db.session.add(user)
            db.session.flush()  # Get user.id
            instructor.user_id = user.id

        db.session.add(instructor)
        db.session.commit()
        return instructor

    def update_instructor(self, tenant_id: str, instructor_id: str, data: dict) -> Instructor:
        """Update an existing instructor."""
        instructor = Instructor.query.filter_by(id=instructor_id, tenant_id=tenant_id).first()
        if not instructor:
            raise NotFound('Instructor not found')

        if data.get('position') and data['position'] not in Instructor.VALID_POSITIONS:
            raise ValidationError(f"Invalid position. Must be one of: {', '.join(Instructor.VALID_POSITIONS)}")

        # Update fields
        updatable = {
            'firstName': 'first_name', 'lastName': 'last_name',
            'personalNumber': 'personal_number', 'email': 'email',
            'phone': 'phone', 'position': 'position',
            'licenseInfo': 'license_info', 'licenseExpiry': 'license_expiry',
            'costPerCandidate': 'cost_per_candidate',
            'isActive': 'is_active',
        }
        for schema_field, model_field in updatable.items():
            if schema_field in data and data[schema_field] is not None:
                setattr(instructor, model_field, data[schema_field])

        # Handle password update for linked user
        if data.get('password') and instructor.user_id:
            user = User.query.get(instructor.user_id)
            if user:
                user.set_password(data['password'])

        # Handle creating login if email+password provided and no user yet
        if data.get('email') and data.get('password') and not instructor.user_id:
            user = User(
                tenant_id=tenant_id,
                username=data['email'],
                full_name=instructor.full_name,
                email=data['email'],
                role='instructor',
            )
            user.set_password(data['password'])
            db.session.add(user)
            db.session.flush()
            instructor.user_id = user.id

        db.session.commit()
        return instructor

    def delete_instructor(self, tenant_id: str, instructor_id: str) -> None:
        """Soft-delete (deactivate) an instructor."""
        instructor = Instructor.query.filter_by(id=instructor_id, tenant_id=tenant_id).first()
        if not instructor:
            raise NotFound('Instructor not found')
        instructor.is_active = False
        if instructor.user_id:
            user = User.query.get(instructor.user_id)
            if user:
                user.is_active = False
        db.session.commit()

    def get_instructor_for_user(self, user_id: str, tenant_id: str) -> Instructor:
        """Get instructor record linked to a user account."""
        instructor = Instructor.query.filter_by(user_id=user_id, tenant_id=tenant_id).first()
        if not instructor:
            raise NotFound('Instructor profile not found')
        return instructor
