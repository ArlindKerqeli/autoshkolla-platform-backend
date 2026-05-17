from flask import request, g, jsonify
from datetime import datetime, date
from app.api import api_bp
from app.models.payment_model import Payment
from app.models.candidate_model import Candidate
from app.schemas.payments import CreatePaymentSchema, RecordPaymentSchema
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


@api_bp.get('/payments')
def list_payments():
    """List payments for a candidate."""
    candidate_id = request.args.get('candidateId')
    if not candidate_id:
        raise ValidationError('candidateId is required')

    # Verify candidate belongs to tenant
    candidate = Candidate.query.filter_by(
        id=candidate_id, tenant_id=g.tenant_id, deleted_at=None
    ).first()
    if not candidate:
        raise NotFound('Candidate not found')

    # Build query
    query = Payment.query.filter_by(
        candidate_id=candidate_id, tenant_id=g.tenant_id
    )

    # Optional date filters
    start_date = request.args.get('startDate')
    if start_date:
        query = query.filter(Payment.payment_date >= _parse_date(start_date))

    end_date = request.args.get('endDate')
    if end_date:
        query = query.filter(Payment.payment_date <= _parse_date(end_date))

    query = query.order_by(Payment.payment_date.desc())
    result = paginate_query(query)
    result['data'] = [p.to_dict() for p in result['data']]
    return result


@api_bp.get('/payments/<payment_id>')
def get_payment(payment_id):
    """Get a specific payment."""
    payment = Payment.query.filter_by(
        id=payment_id, tenant_id=g.tenant_id
    ).first()
    if not payment:
        raise NotFound('Payment not found')

    return jsonify(payment.to_dict())


@api_bp.post('/payments')
def create_payment():
    """Create a new payment and update candidate amount_paid."""
    _require_admin()
    payload = parse_body(CreatePaymentSchema, request.get_json(silent=True) or {})

    # Verify candidate exists and belongs to tenant
    candidate = Candidate.query.filter_by(
        id=payload.candidateId, tenant_id=g.tenant_id, deleted_at=None
    ).first()
    if not candidate:
        raise NotFound('Candidate not found')

    if payload.amount is None or float(payload.amount) <= 0:
        raise ValidationError('Payment amount must be greater than 0')

    payment = Payment(
        candidate_id=payload.candidateId,
        tenant_id=g.tenant_id,
        amount=payload.amount,
        payment_method=payload.paymentMethod,
        payment_date=_parse_date(payload.paymentDate),
        received_by_user_id=g.current_user['sub'],
        is_supplementary=payload.isSupplementary or False,
        remarks=payload.remarks,
    )
    db.session.add(payment)

    # Update candidate amount paid
    candidate.amount_paid = (float(candidate.amount_paid or 0)) + float(payload.amount)

    db.session.commit()
    return jsonify(payment.to_dict()), 201


@api_bp.delete('/payments/<payment_id>')
def delete_payment(payment_id):
    """Delete a payment and update candidate amount_paid."""
    _require_admin()
    payment = Payment.query.filter_by(
        id=payment_id, tenant_id=g.tenant_id
    ).first()
    if not payment:
        raise NotFound('Payment not found')

    # Update candidate amount paid
    candidate = payment.candidate
    candidate.amount_paid = max(0, float(candidate.amount_paid or 0) - float(payment.amount))

    db.session.delete(payment)
    db.session.commit()
    return '', 204


@api_bp.get('/payments/summary')
def payment_summary():
    """Get payment summary for a date range."""
    _require_admin()

    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')

    query = Payment.query.filter_by(tenant_id=g.tenant_id)

    if start_date:
        query = query.filter(Payment.payment_date >= _parse_date(start_date))
    if end_date:
        query = query.filter(Payment.payment_date <= _parse_date(end_date))

    payments = query.all()

    total_amount = sum(float(p.amount or 0) for p in payments)
    total_by_method = {}
    total_supplementary = 0

    for payment in payments:
        method = payment.payment_method or 'Unknown'
        total_by_method[method] = total_by_method.get(method, 0) + float(payment.amount or 0)
        if payment.is_supplementary:
            total_supplementary += float(payment.amount or 0)

    return jsonify({
        'totalAmount': total_amount,
        'totalByMethod': total_by_method,
        'totalSupplementary': total_supplementary,
        'count': len(payments),
    })
