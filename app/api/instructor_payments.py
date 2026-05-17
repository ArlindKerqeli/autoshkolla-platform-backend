from datetime import datetime, date
from flask import request, g
from app.api import api_bp
from app.models.instructor_model import Instructor
from app.models.instructor_payment_model import InstructorPayment
from app.utils.pagination import paginate_query
from app.middleware.error_handler import NotFound, Forbidden, ValidationError
from app.utils.db import db
from sqlalchemy import func


def _require_admin():
    if g.current_user.get('role') not in ('administrator', 'super_admin'):
        raise Forbidden('Administrator access required')


@api_bp.get('/instructors/debt-summaries')
def get_all_debt_summaries():
    """Get debt summaries for all instructors in the tenant."""
    _require_admin()
    instructors = Instructor.query.filter_by(tenant_id=g.tenant_id, is_active=True).order_by(
        Instructor.last_name, Instructor.first_name
    ).all()

    summaries = []
    for instructor in instructors:
        summary = InstructorPayment.query.filter_by(
            instructor_id=instructor.id, tenant_id=g.tenant_id
        ).with_entities(
            func.count().label('total_candidates'),
            func.coalesce(func.sum(InstructorPayment.amount), 0).label('total_owed'),
            func.coalesce(func.sum(InstructorPayment.amount_paid), 0).label('total_paid'),
        ).first()

        total_owed = float(summary.total_owed) if summary else 0
        total_paid = float(summary.total_paid) if summary else 0
        summaries.append({
            'instructorId': str(instructor.id),
            'instructorName': instructor.full_name,
            'totalCandidates': summary.total_candidates if summary else 0,
            'totalAmountOwed': total_owed,
            'totalAmountPaid': total_paid,
            'outstandingBalance': total_owed - total_paid,
            'costPerCandidate': float(instructor.cost_per_candidate) if instructor.cost_per_candidate else 65.00,
        })

    return summaries


@api_bp.get('/instructors/<instructor_id>/debt-summary')
def get_instructor_debt_summary(instructor_id):
    instructor = Instructor.query.filter_by(id=instructor_id, tenant_id=g.tenant_id).first()
    if not instructor:
        raise NotFound('Instructor not found')

    # Verify access: admin can see all, instructor can see own
    if g.current_user.get('role') == 'instructor':
        if not instructor.user_id or str(instructor.user_id) != g.current_user['sub']:
            raise Forbidden('Access denied')

    summary = InstructorPayment.query.filter_by(
        instructor_id=instructor.id, tenant_id=g.tenant_id
    ).with_entities(
        func.count().label('total_candidates'),
        func.coalesce(func.sum(InstructorPayment.amount), 0).label('total_owed'),
        func.coalesce(func.sum(InstructorPayment.amount_paid), 0).label('total_paid'),
    ).first()

    return {
        'instructorId': str(instructor.id),
        'instructorName': instructor.full_name,
        'totalCandidates': summary.total_candidates,
        'totalAmountOwed': float(summary.total_owed),
        'totalAmountPaid': float(summary.total_paid),
        'outstandingBalance': float(summary.total_owed) - float(summary.total_paid),
        'costPerCandidate': float(instructor.cost_per_candidate) if instructor.cost_per_candidate else 65.00,
    }


@api_bp.get('/instructors/<instructor_id>/payments')
def get_instructor_payments(instructor_id):
    instructor = Instructor.query.filter_by(id=instructor_id, tenant_id=g.tenant_id).first()
    if not instructor:
        raise NotFound('Instructor not found')

    query = InstructorPayment.query.filter_by(
        instructor_id=instructor.id, tenant_id=g.tenant_id
    )

    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    query = query.order_by(InstructorPayment.created_at.desc())
    result = paginate_query(query)
    result['data'] = [p.to_dict() for p in result['data']]
    return result


@api_bp.post('/instructors/<instructor_id>/payments')
def record_instructor_payment(instructor_id):
    _require_admin()
    instructor = Instructor.query.filter_by(id=instructor_id, tenant_id=g.tenant_id).first()
    if not instructor:
        raise NotFound('Instructor not found')

    data = request.get_json(silent=True) or {}
    candidate_id = data.get('candidateId') or data.get('candidate_id')
    amount = data.get('amount')

    if not candidate_id or not amount:
        raise ValidationError('candidateId and amount are required')

    payment = InstructorPayment.query.filter_by(
        instructor_id=instructor.id,
        candidate_id=candidate_id,
        tenant_id=g.tenant_id
    ).first()
    if not payment:
        raise NotFound('No payment record found for this instructor-candidate pair')

    payment.amount_paid = float(payment.amount_paid or 0) + float(amount)
    payment.payment_date = date.today()
    payment.payment_method = data.get('paymentMethod') or data.get('payment_method')
    payment.remarks = data.get('remarks')

    if float(payment.amount_paid) >= float(payment.amount):
        payment.status = 'paid'
    elif float(payment.amount_paid) > 0:
        payment.status = 'partial'

    db.session.commit()
    return payment.to_dict(), 201
