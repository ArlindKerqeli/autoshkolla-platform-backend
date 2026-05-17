from datetime import datetime, date, timedelta
from flask import request, g
from app.api import api_bp
from app.models.candidate_model import Candidate
from app.models.instructor_model import Instructor
from app.models.instructor_payment_model import InstructorPayment
from app.models.scheduled_lesson_model import ScheduledLesson
from app.models.vehicle_model import Vehicle
from app.models.category_model import Category
from app.middleware.error_handler import Forbidden
from app.utils.db import db
from sqlalchemy import func


def _require_admin():
    if g.current_user.get('role') not in ('administrator', 'super_admin'):
        raise Forbidden('Administrator access required')


@api_bp.get('/dashboard/stats')
def dashboard_stats():
    _require_admin()
    tid = g.tenant_id
    today = date.today()
    month_start = today.replace(day=1)
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)

    # Total candidates (not deleted)
    total = Candidate.query.filter_by(
        tenant_id=tid, deleted_at=None
    ).count()

    # Active candidates
    active = Candidate.query.filter_by(
        tenant_id=tid, is_archived=False, deleted_at=None
    ).count()

    # Archived candidates
    archived = Candidate.query.filter_by(
        tenant_id=tid, is_archived=True, deleted_at=None
    ).count()

    active_last_month = Candidate.query.filter(
        Candidate.tenant_id == tid,
        Candidate.is_archived == False,
        Candidate.deleted_at == None,
        Candidate.created_at < month_start
    ).count()

    # Revenue and pending payments
    from app.models.payment_model import Payment
    monthly_rev = 0
    total_revenue = 0
    monthly_trend = 0
    try:
        # Total revenue (all time)
        total_rev_result = db.session.query(
            func.coalesce(func.sum(Payment.amount), 0)
        ).filter(Payment.tenant_id == tid).scalar()
        total_revenue = float(total_rev_result)

        # Monthly revenue
        rev = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
            Payment.tenant_id == tid,
            Payment.payment_date >= month_start,
        ).scalar()
        monthly_rev = float(rev)
        last_rev = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
            Payment.tenant_id == tid,
            Payment.payment_date >= last_month_start,
            Payment.payment_date < month_start,
        ).scalar()
        if float(last_rev) > 0:
            monthly_trend = ((monthly_rev - float(last_rev)) / float(last_rev)) * 100
    except (ImportError, AttributeError, TypeError):
        pass

    # Pending payments (sum of price - amount_paid for active candidates)
    pending_result = db.session.query(
        func.coalesce(func.sum(Candidate.price - Candidate.amount_paid), 0)
    ).filter(
        Candidate.tenant_id == tid,
        Candidate.is_archived == False,
        Candidate.deleted_at == None,
    ).scalar()
    pending_payments = float(pending_result) if pending_result else 0

    # Practical hours today
    hours_today = ScheduledLesson.query.filter_by(
        tenant_id=tid, scheduled_date=today, status='scheduled'
    ).count()

    # Instructor debt total
    debt = db.session.query(
        func.coalesce(func.sum(InstructorPayment.amount), 0) -
        func.coalesce(func.sum(InstructorPayment.amount_paid), 0)
    ).filter(InstructorPayment.tenant_id == tid).scalar()

    # Recent candidates (last 5 registered)
    recent = Candidate.query.filter_by(
        tenant_id=tid, deleted_at=None
    ).order_by(Candidate.registration_date.desc(), Candidate.created_at.desc()).limit(5).all()

    recent_candidates = []
    for c in recent:
        recent_candidates.append({
            'id': str(c.id),
            'fullName': c.full_name,
            'registrationDate': c.registration_date.isoformat() if c.registration_date else None,
            'categoryCode': c.category.code if c.category else None,
            'isArchived': c.is_archived,
        })

    return {
        'totalCandidates': total,
        'activeCandidates': active,
        'archivedCandidates': archived,
        'activeCandidatesTrend': active - active_last_month,
        'totalRevenue': total_revenue,
        'monthlyRevenue': monthly_rev,
        'monthlyRevenueTrend': round(monthly_trend, 1),
        'pendingPayments': pending_payments,
        'practicalHoursToday': hours_today,
        'instructorTotalDebt': float(debt) if debt else 0,
        'recentCandidates': recent_candidates,
    }


@api_bp.get('/dashboard/category-breakdown')
def dashboard_category_breakdown():
    _require_admin()
    tid = g.tenant_id

    results = db.session.query(
        Category.code,
        func.count(Candidate.id).label('count')
    ).join(Candidate, Candidate.category_id == Category.id).filter(
        Candidate.tenant_id == tid,
        Candidate.is_archived == False,
        Candidate.deleted_at == None,
    ).group_by(Category.code).all()

    total = sum(r.count for r in results)
    data = []
    for r in results:
        pct = (r.count / total * 100) if total > 0 else 0
        data.append({
            'category': r.code,
            'count': r.count,
            'percentage': round(pct, 1),
        })

    return data


@api_bp.get('/dashboard/today-schedule')
def dashboard_today_schedule():
    _require_admin()
    today = date.today()
    lessons = ScheduledLesson.query.filter_by(
        tenant_id=g.tenant_id, scheduled_date=today
    ).order_by(ScheduledLesson.start_time).limit(20).all()

    return [l.to_dict() for l in lessons]


def _expiry_severity(days_left):
    """Return severity level based on days remaining until expiry."""
    if days_left < 0:
        return 'error'
    elif days_left <= 7:
        return 'error'
    elif days_left <= 15:
        return 'warning'
    else:
        return 'info'


def _vehicle_expiry_alerts(tid, today):
    """Generate alerts for vehicles with expiring registration, technical control, or insurance."""
    alert_threshold = today + timedelta(days=30)
    alerts = []

    vehicles = Vehicle.query.filter(
        Vehicle.tenant_id == tid,
        Vehicle.is_active == True,
    ).all()

    for v in vehicles:
        if v.registration_expiry and v.registration_expiry <= alert_threshold:
            days = (v.registration_expiry - today).days
            severity = _expiry_severity(days)
            if days < 0:
                msg = f"Regjistrimi i automjetit {v.plate_number} ka skaduar ({v.registration_expiry.strftime('%d.%m.%Y')})"
            elif days == 0:
                msg = f"Regjistrimi i automjetit {v.plate_number} skadon sot"
            else:
                msg = f"Regjistrimi i automjetit {v.plate_number} skadon për {days} ditë ({v.registration_expiry.strftime('%d.%m.%Y')})"
            alerts.append({
                'type': 'expiring_registration',
                'message': msg,
                'entityId': str(v.id),
                'severity': severity,
            })

        if v.technical_control_date and v.technical_control_date <= alert_threshold:
            days = (v.technical_control_date - today).days
            severity = _expiry_severity(days)
            if days < 0:
                msg = f"Kontrolli teknik i automjetit {v.plate_number} ka skaduar ({v.technical_control_date.strftime('%d.%m.%Y')})"
            elif days == 0:
                msg = f"Kontrolli teknik i automjetit {v.plate_number} skadon sot"
            else:
                msg = f"Kontrolli teknik i automjetit {v.plate_number} skadon për {days} ditë ({v.technical_control_date.strftime('%d.%m.%Y')})"
            alerts.append({
                'type': 'expiring_technical_control',
                'message': msg,
                'entityId': str(v.id),
                'severity': severity,
            })

        if v.insurance_expiry and v.insurance_expiry <= alert_threshold:
            days = (v.insurance_expiry - today).days
            severity = _expiry_severity(days)
            if days < 0:
                msg = f"Sigurimi i automjetit {v.plate_number} ka skaduar ({v.insurance_expiry.strftime('%d.%m.%Y')})"
            elif days == 0:
                msg = f"Sigurimi i automjetit {v.plate_number} skadon sot"
            else:
                msg = f"Sigurimi i automjetit {v.plate_number} skadon për {days} ditë ({v.insurance_expiry.strftime('%d.%m.%Y')})"
            alerts.append({
                'type': 'expiring_insurance',
                'message': msg,
                'entityId': str(v.id),
                'severity': severity,
            })

    return alerts


def _instructor_license_alerts(tenant_id, today):
    """Generate alerts for instructors with expiring licenses."""
    alerts = []
    threshold = today + timedelta(days=30)
    instructors = Instructor.query.filter(
        Instructor.tenant_id == tenant_id,
        Instructor.is_active == True,
        Instructor.license_expiry != None,
        Instructor.license_expiry <= threshold,
    ).all()

    for inst in instructors:
        days_left = (inst.license_expiry - today).days
        severity = _expiry_severity(days_left)
        if days_left < 0:
            msg = f"Licenca e instruktorit {inst.first_name} {inst.last_name} ka skaduar ({inst.license_expiry.strftime('%d.%m.%Y')})"
        elif days_left == 0:
            msg = f"Licenca e instruktorit {inst.first_name} {inst.last_name} skadon sot"
        else:
            msg = f"Licenca e instruktorit {inst.first_name} {inst.last_name} skadon për {days_left} ditë ({inst.license_expiry.strftime('%d.%m.%Y')})"

        alerts.append({
            'type': 'expiring_instructor_license',
            'message': msg,
            'entityId': str(inst.id),
            'severity': severity,
        })
    return alerts


@api_bp.get('/dashboard/alerts')
def dashboard_alerts():
    _require_admin()
    tid = g.tenant_id
    today = date.today()

    alerts = []

    # Vehicle registration + technical control + insurance expiry
    alerts.extend(_vehicle_expiry_alerts(tid, today))

    # Instructor license expiry
    alerts.extend(_instructor_license_alerts(tid, today))

    # Candidates with overdue payments (debt > 0, registered > 30 days ago)
    overdue_threshold = today - timedelta(days=30)
    overdue_candidates = Candidate.query.filter(
        Candidate.tenant_id == tid,
        Candidate.is_archived == False,
        Candidate.deleted_at == None,
        Candidate.registration_date <= overdue_threshold,
    ).all()
    for c in overdue_candidates:
        if c.debt > 0:
            days = (today - c.registration_date).days
            alerts.append({
                'type': 'overdue_payment',
                'message': f"{c.full_name} ka borxh €{c.debt:.2f} ({days} ditë pa paguar)",
                'entityId': str(c.id),
                'severity': 'warning',
            })

    # Instructors with high debt
    instructor_debts = db.session.query(
        Instructor.id, Instructor.first_name, Instructor.last_name,
        (func.coalesce(func.sum(InstructorPayment.amount), 0) -
         func.coalesce(func.sum(InstructorPayment.amount_paid), 0)).label('outstanding')
    ).join(InstructorPayment, InstructorPayment.instructor_id == Instructor.id).filter(
        Instructor.tenant_id == tid,
        Instructor.is_active == True,
    ).group_by(Instructor.id).having(
        func.coalesce(func.sum(InstructorPayment.amount), 0) -
        func.coalesce(func.sum(InstructorPayment.amount_paid), 0) > 0
    ).all()

    for d in instructor_debts:
        alerts.append({
            'type': 'instructor_high_debt',
            'message': f"Instruktori {d.first_name} {d.last_name} ka borxh €{float(d.outstanding):.2f}",
            'entityId': str(d.id),
            'severity': 'info',
        })

    # Sort: errors first, then warnings, then info
    severity_order = {'error': 0, 'warning': 1, 'info': 2}
    alerts.sort(key=lambda a: severity_order.get(a['severity'], 3))

    return alerts
