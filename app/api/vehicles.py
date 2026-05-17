from flask import request, g
from app.api import api_bp
from app.models.vehicle_model import Vehicle
from app.schemas.vehicles import CreateVehicleSchema, UpdateVehicleSchema
from app.utils.validation import parse_body
from app.utils.pagination import paginate_query
from app.middleware.error_handler import NotFound, Forbidden
from app.utils.db import db


def _require_admin():
    if g.current_user.get('role') not in ('administrator', 'super_admin'):
        raise Forbidden('Administrator access required')


@api_bp.get('/vehicles')
def get_vehicles():
    query = Vehicle.query.filter_by(tenant_id=g.tenant_id)
    active = request.args.get('active')
    if active is not None:
        query = query.filter_by(is_active=active.lower() == 'true')
    instructor_id = request.args.get('instructor_id')
    if instructor_id:
        query = query.filter_by(instructor_id=instructor_id)
    query = query.order_by(Vehicle.plate_number)
    result = paginate_query(query)
    result['data'] = [v.to_dict() for v in result['data']]
    return result


@api_bp.get('/vehicles/<vehicle_id>')
def get_vehicle(vehicle_id):
    vehicle = Vehicle.query.filter_by(id=vehicle_id, tenant_id=g.tenant_id).first()
    if not vehicle:
        raise NotFound('Vehicle not found')
    return vehicle.to_dict()


@api_bp.post('/vehicles')
def create_vehicle():
    _require_admin()
    payload = parse_body(CreateVehicleSchema, request.get_json(silent=True) or {})
    vehicle = Vehicle(
        tenant_id=g.tenant_id,
        make=payload.make,
        model=payload.model,
        chassis_number=payload.chassisNumber,
        plate_number=payload.plateNumber,
        registration_date=payload.registrationDate,
        registration_expiry=payload.registrationExpiry,
        technical_control_date=payload.technicalControlDate,
        insurance_expiry=payload.insuranceExpiry,
        instructor_id=payload.instructorId,
    )
    db.session.add(vehicle)
    db.session.commit()
    return vehicle.to_dict(), 201


@api_bp.put('/vehicles/<vehicle_id>')
def update_vehicle(vehicle_id):
    _require_admin()
    vehicle = Vehicle.query.filter_by(id=vehicle_id, tenant_id=g.tenant_id).first()
    if not vehicle:
        raise NotFound('Vehicle not found')
    payload = parse_body(UpdateVehicleSchema, request.get_json(silent=True) or {})
    update_data = payload.model_dump(exclude_none=True)
    field_map = {
        'make': 'make', 'model': 'model', 'chassisNumber': 'chassis_number',
        'plateNumber': 'plate_number', 'registrationDate': 'registration_date',
        'registrationExpiry': 'registration_expiry', 'technicalControlDate': 'technical_control_date',
        'insuranceExpiry': 'insurance_expiry', 'instructorId': 'instructor_id', 'isActive': 'is_active',
    }
    for schema_key, model_key in field_map.items():
        if schema_key in update_data:
            setattr(vehicle, model_key, update_data[schema_key])
    db.session.commit()
    return vehicle.to_dict()


@api_bp.delete('/vehicles/<vehicle_id>')
def delete_vehicle(vehicle_id):
    _require_admin()
    vehicle = Vehicle.query.filter_by(id=vehicle_id, tenant_id=g.tenant_id).first()
    if not vehicle:
        raise NotFound('Vehicle not found')
    vehicle.is_active = False
    db.session.commit()
    return '', 204
