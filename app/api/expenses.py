from flask import request, g, jsonify
from datetime import datetime, date
from app.api import api_bp
from app.models.expense_model import Expense
from app.models.expense_type_model import ExpenseType
from app.models.vehicle_model import Vehicle
from app.schemas.expenses import (
    CreateExpenseTypeSchema,
    UpdateExpenseTypeSchema,
    CreateExpenseSchema,
    UpdateExpenseSchema,
)
from app.utils.validation import parse_body, ValidationError
from app.utils.pagination import paginate_query
from app.utils.db import db
from app.middleware.error_handler import NotFound, Forbidden


def _require_admin():
    """Require administrator role."""
    if g.current_user.get('role') not in ('administrator', 'super_admin'):
        raise Forbidden('Administrator access required')


def _parse_date(date_str: str) -> date:
    """Parse date string (YYYY-MM-DD format) to date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValidationError(f'Invalid date format: {date_str}')


# ==================== EXPENSE TYPES ====================

@api_bp.get('/expense-types')
def list_expense_types():
    """List expense types for tenant."""
    query = ExpenseType.query.filter_by(tenant_id=g.tenant_id).order_by(ExpenseType.name)
    result = paginate_query(query)
    result['data'] = [et.to_dict() for et in result['data']]
    return result


@api_bp.get('/expense-types/<expense_type_id>')
def get_expense_type(expense_type_id):
    """Get a specific expense type."""
    expense_type = ExpenseType.query.filter_by(
        id=expense_type_id, tenant_id=g.tenant_id
    ).first()
    if not expense_type:
        raise NotFound('Expense type not found')

    return jsonify(expense_type.to_dict())


@api_bp.post('/expense-types')
def create_expense_type():
    """Create a new expense type."""
    _require_admin()
    payload = parse_body(CreateExpenseTypeSchema, request.get_json(silent=True) or {})

    # Check if name already exists for this tenant
    existing = ExpenseType.query.filter_by(
        tenant_id=g.tenant_id, name=payload.name
    ).first()
    if existing:
        raise ValidationError(f'Expense type "{payload.name}" already exists')

    expense_type = ExpenseType(
        tenant_id=g.tenant_id,
        name=payload.name,
        is_active=payload.isActive if payload.isActive is not None else True,
    )
    db.session.add(expense_type)
    db.session.commit()

    return jsonify(expense_type.to_dict()), 201


@api_bp.put('/expense-types/<expense_type_id>')
def update_expense_type(expense_type_id):
    """Update an expense type."""
    _require_admin()
    expense_type = ExpenseType.query.filter_by(
        id=expense_type_id, tenant_id=g.tenant_id
    ).first()
    if not expense_type:
        raise NotFound('Expense type not found')

    payload = parse_body(UpdateExpenseTypeSchema, request.get_json(silent=True) or {})

    if payload.name is not None:
        # Check if new name already exists
        existing = ExpenseType.query.filter_by(
            tenant_id=g.tenant_id, name=payload.name
        ).filter(ExpenseType.id != expense_type_id).first()
        if existing:
            raise ValidationError(f'Expense type "{payload.name}" already exists')
        expense_type.name = payload.name

    if payload.isActive is not None:
        expense_type.is_active = payload.isActive

    db.session.commit()
    return jsonify(expense_type.to_dict())


@api_bp.delete('/expense-types/<expense_type_id>')
def delete_expense_type(expense_type_id):
    """Delete an expense type."""
    _require_admin()
    expense_type = ExpenseType.query.filter_by(
        id=expense_type_id, tenant_id=g.tenant_id
    ).first()
    if not expense_type:
        raise NotFound('Expense type not found')

    # Check if any expenses use this type
    expense_count = Expense.query.filter_by(expense_type_id=expense_type_id).count()
    if expense_count > 0:
        raise ValidationError(f'Cannot delete expense type with {expense_count} associated expense(s)')

    db.session.delete(expense_type)
    db.session.commit()
    return '', 204


# ==================== EXPENSES ====================

@api_bp.get('/expenses')
def list_expenses():
    """List expenses with optional filters."""
    _require_admin()

    query = Expense.query.filter_by(tenant_id=g.tenant_id)

    # Optional date filters
    start_date = request.args.get('startDate')
    if start_date:
        query = query.filter(Expense.date >= _parse_date(start_date))

    end_date = request.args.get('endDate')
    if end_date:
        query = query.filter(Expense.date <= _parse_date(end_date))

    # Optional vehicle filter
    vehicle_id = request.args.get('vehicleId')
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)

    # Optional expense type filter
    expense_type_id = request.args.get('expenseTypeId')
    if expense_type_id:
        query = query.filter_by(expense_type_id=expense_type_id)

    query = query.order_by(Expense.date.desc())
    result = paginate_query(query)
    result['data'] = [e.to_dict() for e in result['data']]
    return result


@api_bp.get('/expenses/<expense_id>')
def get_expense(expense_id):
    """Get a specific expense."""
    expense = Expense.query.filter_by(
        id=expense_id, tenant_id=g.tenant_id
    ).first()
    if not expense:
        raise NotFound('Expense not found')

    return jsonify(expense.to_dict())


@api_bp.post('/expenses')
def create_expense():
    """Create a new expense."""
    _require_admin()
    payload = parse_body(CreateExpenseSchema, request.get_json(silent=True) or {})

    # Verify expense type exists
    expense_type = ExpenseType.query.filter_by(
        id=payload.expenseTypeId, tenant_id=g.tenant_id
    ).first()
    if not expense_type:
        raise NotFound('Expense type not found')

    # Verify vehicle if provided
    if payload.vehicleId:
        vehicle = Vehicle.query.filter_by(
            id=payload.vehicleId, tenant_id=g.tenant_id
        ).first()
        if not vehicle:
            raise NotFound('Vehicle not found')

    if payload.amount is None or float(payload.amount) <= 0:
        raise ValidationError('Expense amount must be greater than 0')

    expense = Expense(
        tenant_id=g.tenant_id,
        vehicle_id=payload.vehicleId,
        expense_type_id=payload.expenseTypeId,
        date=_parse_date(payload.date),
        amount=payload.amount,
        description=payload.description,
    )
    db.session.add(expense)
    db.session.commit()

    return jsonify(expense.to_dict()), 201


@api_bp.put('/expenses/<expense_id>')
def update_expense(expense_id):
    """Update an expense."""
    _require_admin()
    expense = Expense.query.filter_by(
        id=expense_id, tenant_id=g.tenant_id
    ).first()
    if not expense:
        raise NotFound('Expense not found')

    payload = parse_body(UpdateExpenseSchema, request.get_json(silent=True) or {})

    if payload.vehicleId is not None:
        if payload.vehicleId:
            vehicle = Vehicle.query.filter_by(
                id=payload.vehicleId, tenant_id=g.tenant_id
            ).first()
            if not vehicle:
                raise NotFound('Vehicle not found')
        expense.vehicle_id = payload.vehicleId

    if payload.expenseTypeId is not None:
        expense_type = ExpenseType.query.filter_by(
            id=payload.expenseTypeId, tenant_id=g.tenant_id
        ).first()
        if not expense_type:
            raise NotFound('Expense type not found')
        expense.expense_type_id = payload.expenseTypeId

    if payload.date is not None:
        expense.date = _parse_date(payload.date)
    if payload.amount is not None:
        expense.amount = payload.amount
    if payload.description is not None:
        expense.description = payload.description

    db.session.commit()
    return jsonify(expense.to_dict())


@api_bp.delete('/expenses/<expense_id>')
def delete_expense(expense_id):
    """Delete an expense."""
    _require_admin()
    expense = Expense.query.filter_by(
        id=expense_id, tenant_id=g.tenant_id
    ).first()
    if not expense:
        raise NotFound('Expense not found')

    db.session.delete(expense)
    db.session.commit()
    return '', 204


@api_bp.get('/expenses-summary')
def expenses_summary():
    """Get expense summary for a date range."""
    _require_admin()

    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')

    query = Expense.query.filter_by(tenant_id=g.tenant_id)

    if start_date:
        query = query.filter(Expense.date >= _parse_date(start_date))
    if end_date:
        query = query.filter(Expense.date <= _parse_date(end_date))

    expenses = query.all()

    total_amount = sum(float(e.amount or 0) for e in expenses)

    # Group by expense type
    by_type = {}
    for expense in expenses:
        type_name = expense.expense_type.name if expense.expense_type else 'Unknown'
        if type_name not in by_type:
            by_type[type_name] = {'count': 0, 'amount': 0}
        by_type[type_name]['count'] += 1
        by_type[type_name]['amount'] += float(expense.amount or 0)

    # Group by vehicle
    by_vehicle = {}
    for expense in expenses:
        vehicle_plate = expense.vehicle.plate_number if expense.vehicle else 'No Vehicle'
        if vehicle_plate not in by_vehicle:
            by_vehicle[vehicle_plate] = {'count': 0, 'amount': 0}
        by_vehicle[vehicle_plate]['count'] += 1
        by_vehicle[vehicle_plate]['amount'] += float(expense.amount or 0)

    return jsonify({
        'totalAmount': total_amount,
        'totalCount': len(expenses),
        'byType': by_type,
        'byVehicle': by_vehicle,
    })
