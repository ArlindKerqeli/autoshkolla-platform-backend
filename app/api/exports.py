"""Export endpoints for Excel/CSV download of tenant data."""

from datetime import datetime, date
from flask import request, g
from sqlalchemy import func

from app.api import api_bp
from app.models.candidate_model import Candidate
from app.models.payment_model import Payment
from app.models.expense_model import Expense
from app.models.expense_type_model import ExpenseType
from app.models.instructor_model import Instructor
from app.models.vehicle_model import Vehicle
from app.models.instructor_payment_model import InstructorPayment
from app.models.theory_hour_session_model import TheoryHourSession
from app.models.practical_hour_session_model import PracticalHourSession
from app.models.exam_model import Exam
from app.middleware.error_handler import Forbidden, NotFound
from app.utils.validation import ValidationError
from app.utils.db import db
from app.services.export_service import (
    ExportColumn,
    format_date,
    format_currency,
    format_boolean,
    generate_excel,
    generate_csv,
    make_export_response,
)


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


def _get_format() -> str:
    """Get export format from query params, default xlsx."""
    fmt = request.args.get('format', 'xlsx').lower()
    if fmt not in ('xlsx', 'csv'):
        fmt = 'xlsx'
    return fmt


def _build_export(rows: list[dict], columns: list[ExportColumn],
                  filename: str, fmt: str, sheet_name: str = 'Data'):
    """Build export content and return response."""
    if fmt == 'csv':
        content = generate_csv(rows, columns)
    else:
        content = generate_excel(rows, columns, sheet_name=sheet_name)
    return make_export_response(content, filename, fmt)


# ==================== CANDIDATES EXPORT ====================

@api_bp.get('/export/candidates')
def export_candidates():
    """Export candidates list to Excel/CSV."""
    fmt = _get_format()

    query = Candidate.query.filter_by(tenant_id=g.tenant_id, deleted_at=None)

    # Filters — same as candidates.py list endpoint
    is_archived = request.args.get('archived', 'false').lower() == 'true'
    query = query.filter_by(is_archived=is_archived)

    category_id = request.args.get('category_id')
    if category_id:
        query = query.filter_by(category_id=category_id)

    instructor_id = request.args.get('instructor_id')
    if instructor_id:
        query = query.filter_by(instructor_id=instructor_id)

    search = request.args.get('search')
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                Candidate.first_name.ilike(search_term),
                Candidate.last_name.ilike(search_term),
                Candidate.personal_number.ilike(search_term),
                Candidate.phone.ilike(search_term),
                Candidate.protocol_number.ilike(search_term),
            )
        )

    gender = request.args.get('gender')
    if gender:
        query = query.filter_by(gender=gender)

    date_from = request.args.get('date_from')
    if date_from:
        query = query.filter(Candidate.registration_date >= date_from)

    date_to = request.args.get('date_to')
    if date_to:
        query = query.filter(Candidate.registration_date <= date_to)

    query = query.order_by(Candidate.registration_date.desc())
    candidates = query.all()

    rows = []
    for c in candidates:
        rows.append({
            'protocol_number': c.protocol_number or '',
            'first_name': c.first_name,
            'last_name': c.last_name,
            'personal_number': c.personal_number,
            'gender': 'M' if c.gender == 'M' else ('F' if c.gender == 'F' else ''),
            'phone': c.phone or '',
            'email': c.email or '',
            'category': c.category.code if c.category else '',
            'instructor': c.instructor.full_name if c.instructor else '',
            'price': float(c.price) if c.price else 0,
            'amount_paid': float(c.amount_paid) if c.amount_paid else 0,
            'debt': c.debt,
            'registration_date': c.registration_date,
            'status': 'Arkivuar' if c.is_archived else 'Aktiv',
        })

    columns = [
        ExportColumn(key='protocol_number', header='Nr. Regjistrit', width=15),
        ExportColumn(key='first_name', header='Emri', width=18),
        ExportColumn(key='last_name', header='Mbiemri', width=18),
        ExportColumn(key='personal_number', header='Nr. Personal', width=15),
        ExportColumn(key='gender', header='Gjinia', width=10),
        ExportColumn(key='phone', header='Telefoni', width=15),
        ExportColumn(key='email', header='Email', width=25),
        ExportColumn(key='category', header='Kategoria', width=12),
        ExportColumn(key='instructor', header='Instruktori', width=22),
        ExportColumn(key='price', header='Çmimi', width=12, formatter=format_currency),
        ExportColumn(key='amount_paid', header='Paguar', width=12, formatter=format_currency),
        ExportColumn(key='debt', header='Borxhi', width=12, formatter=format_currency),
        ExportColumn(key='registration_date', header='Data Regjistrimit', width=16, formatter=format_date),
        ExportColumn(key='status', header='Statusi', width=12),
    ]

    return _build_export(rows, columns, 'kandidatet', fmt, sheet_name='Kandidatet')


# ==================== PAYMENTS EXPORT ====================

@api_bp.get('/export/payments')
def export_payments():
    """Export payments list to Excel/CSV."""
    fmt = _get_format()

    candidate_id = request.args.get('candidateId')
    if not candidate_id:
        raise ValidationError('candidateId is required')

    # Verify candidate belongs to tenant
    candidate = Candidate.query.filter_by(
        id=candidate_id, tenant_id=g.tenant_id, deleted_at=None
    ).first()
    if not candidate:
        raise NotFound('Candidate not found')

    query = Payment.query.filter_by(
        candidate_id=candidate_id, tenant_id=g.tenant_id
    )

    start_date = request.args.get('startDate')
    if start_date:
        query = query.filter(Payment.payment_date >= _parse_date(start_date))

    end_date = request.args.get('endDate')
    if end_date:
        query = query.filter(Payment.payment_date <= _parse_date(end_date))

    query = query.order_by(Payment.payment_date.desc())
    payments = query.all()

    rows = []
    for p in payments:
        rows.append({
            'candidate': candidate.full_name,
            'amount': float(p.amount) if p.amount else 0,
            'method': p.payment_method or '',
            'date': p.payment_date,
            'received_by': p.received_by.full_name if p.received_by else '',
            'is_supplementary': p.is_supplementary,
            'remarks': p.remarks or '',
        })

    columns = [
        ExportColumn(key='candidate', header='Kandidati', width=25),
        ExportColumn(key='amount', header='Shuma (\u20ac)', width=14, formatter=format_currency),
        ExportColumn(key='method', header='Metoda', width=15),
        ExportColumn(key='date', header='Data', width=14, formatter=format_date),
        ExportColumn(key='received_by', header='Pranuar Nga', width=22),
        ExportColumn(key='is_supplementary', header='Plot\u00ebsues', width=12, formatter=format_boolean),
        ExportColumn(key='remarks', header='V\u00ebrejtje', width=30),
    ]

    filename = f'pagesat_{candidate.first_name}_{candidate.last_name}'
    return _build_export(rows, columns, filename, fmt, sheet_name='Pagesat')


# ==================== EXPENSES EXPORT ====================

@api_bp.get('/export/expenses')
def export_expenses():
    """Export expenses list to Excel/CSV (admin only)."""
    _require_admin()
    fmt = _get_format()

    query = Expense.query.filter_by(tenant_id=g.tenant_id)

    start_date = request.args.get('startDate')
    if start_date:
        query = query.filter(Expense.date >= _parse_date(start_date))

    end_date = request.args.get('endDate')
    if end_date:
        query = query.filter(Expense.date <= _parse_date(end_date))

    vehicle_id = request.args.get('vehicleId')
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)

    expense_type_id = request.args.get('expenseTypeId')
    if expense_type_id:
        query = query.filter_by(expense_type_id=expense_type_id)

    query = query.order_by(Expense.date.desc())
    expenses = query.all()

    rows = []
    for e in expenses:
        rows.append({
            'date': e.date,
            'type': e.expense_type.name if e.expense_type else '',
            'vehicle': e.vehicle.plate_number if e.vehicle else '',
            'amount': float(e.amount) if e.amount else 0,
            'description': e.description or '',
        })

    columns = [
        ExportColumn(key='date', header='Data', width=14, formatter=format_date),
        ExportColumn(key='type', header='Lloji', width=22),
        ExportColumn(key='vehicle', header='Automjeti', width=16),
        ExportColumn(key='amount', header='Shuma (\u20ac)', width=14, formatter=format_currency),
        ExportColumn(key='description', header='P\u00ebrshkrimi', width=35),
    ]

    return _build_export(rows, columns, 'shpenzimet', fmt, sheet_name='Shpenzimet')


# ==================== INSTRUCTORS EXPORT ====================

@api_bp.get('/export/instructors')
def export_instructors():
    """Export instructors list to Excel/CSV."""
    fmt = _get_format()

    query = Instructor.query.filter_by(tenant_id=g.tenant_id)

    active = request.args.get('active')
    if active:
        query = query.filter_by(is_active=active.lower() == 'true')

    position = request.args.get('position')
    if position:
        query = query.filter_by(position=position)

    query = query.order_by(Instructor.last_name, Instructor.first_name)
    instructors = query.all()

    rows = []
    for i in instructors:
        rows.append({
            'code': i.code,
            'first_name': i.first_name,
            'last_name': i.last_name,
            'personal_number': i.personal_number or '',
            'email': i.email or '',
            'phone': i.phone or '',
            'position': i.position,
            'license_expiry': i.license_expiry,
            'cost_per_candidate': float(i.cost_per_candidate) if i.cost_per_candidate else 65.00,
            'status': 'Aktiv' if i.is_active else 'Joaktiv',
        })

    columns = [
        ExportColumn(key='code', header='Kodi', width=12),
        ExportColumn(key='first_name', header='Emri', width=18),
        ExportColumn(key='last_name', header='Mbiemri', width=18),
        ExportColumn(key='personal_number', header='Nr. Personal', width=15),
        ExportColumn(key='email', header='Email', width=25),
        ExportColumn(key='phone', header='Telefoni', width=15),
        ExportColumn(key='position', header='Pozita', width=14),
        ExportColumn(key='license_expiry', header='Licenca Skadon', width=18, formatter=format_date),
        ExportColumn(key='cost_per_candidate', header='Kosto/Kandidat (\u20ac)', width=18, formatter=format_currency),
        ExportColumn(key='status', header='Statusi', width=12),
    ]

    return _build_export(rows, columns, 'instruktoret', fmt, sheet_name='Instruktor\u00ebt')


# ==================== VEHICLES EXPORT ====================

@api_bp.get('/export/vehicles')
def export_vehicles():
    """Export vehicles list to Excel/CSV."""
    fmt = _get_format()

    query = Vehicle.query.filter_by(tenant_id=g.tenant_id)

    active = request.args.get('active')
    if active is not None:
        query = query.filter_by(is_active=active.lower() == 'true')

    instructor_id = request.args.get('instructor_id')
    if instructor_id:
        query = query.filter_by(instructor_id=instructor_id)

    query = query.order_by(Vehicle.plate_number)
    vehicles = query.all()

    rows = []
    for v in vehicles:
        rows.append({
            'make': v.make,
            'model': v.model or '',
            'plate_number': v.plate_number,
            'chassis_number': v.chassis_number or '',
            'instructor': v.instructor.full_name if v.instructor else '',
            'registration_expiry': v.registration_expiry,
            'technical_control_date': v.technical_control_date,
            'insurance_expiry': v.insurance_expiry,
            'status': 'Aktiv' if v.is_active else 'Joaktiv',
        })

    columns = [
        ExportColumn(key='make', header='Marka', width=16),
        ExportColumn(key='model', header='Modeli', width=16),
        ExportColumn(key='plate_number', header='Targa', width=14),
        ExportColumn(key='chassis_number', header='Nr. Shasise', width=22),
        ExportColumn(key='instructor', header='Instruktori', width=22),
        ExportColumn(key='registration_expiry', header='Regjistrimi Skadon', width=18, formatter=format_date),
        ExportColumn(key='technical_control_date', header='Kontrolli Teknik', width=18, formatter=format_date),
        ExportColumn(key='insurance_expiry', header='Sigurimi Skadon', width=18, formatter=format_date),
        ExportColumn(key='status', header='Statusi', width=12),
    ]

    return _build_export(rows, columns, 'automjetet', fmt, sheet_name='Automjetet')


# ==================== INSTRUCTOR DEBT EXPORT ====================

@api_bp.get('/export/instructor-debt')
def export_instructor_debt():
    """Export instructor debt summaries to Excel/CSV (admin only)."""
    _require_admin()
    fmt = _get_format()

    # Replicate the debt summary logic from instructor_payments.py
    instructors = Instructor.query.filter_by(
        tenant_id=g.tenant_id, is_active=True
    ).order_by(Instructor.last_name, Instructor.first_name).all()

    rows = []
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

        rows.append({
            'instructor': instructor.full_name,
            'total_candidates': summary.total_candidates if summary else 0,
            'total_owed': total_owed,
            'total_paid': total_paid,
            'balance': total_owed - total_paid,
        })

    columns = [
        ExportColumn(key='instructor', header='Instruktori', width=25),
        ExportColumn(key='total_candidates', header='Nr. Kandidat\u00ebve', width=18),
        ExportColumn(key='total_owed', header='Shuma Totale (\u20ac)', width=18, formatter=format_currency),
        ExportColumn(key='total_paid', header='E Paguar (\u20ac)', width=16, formatter=format_currency),
        ExportColumn(key='balance', header='Bilanci (\u20ac)', width=16, formatter=format_currency),
    ]

    return _build_export(rows, columns, 'borxhi_instruktoreve', fmt, sheet_name='Borxhi')


# ==================== THEORY HOURS EXPORT ====================

@api_bp.get('/export/theory-hours')
def export_theory_hours():
    """Export theory hour sessions to Excel/CSV."""
    fmt = _get_format()

    candidate_id = request.args.get('candidateId')
    if not candidate_id:
        raise ValidationError('candidateId is required')

    # Verify candidate belongs to tenant
    candidate = Candidate.query.filter_by(
        id=candidate_id, tenant_id=g.tenant_id, deleted_at=None
    ).first()
    if not candidate:
        raise NotFound('Candidate not found')

    # If instructor role, verify candidate is assigned to them
    if g.current_user.get('role') == 'instructor':
        instructor = Instructor.query.filter_by(
            user_id=g.current_user['sub'], tenant_id=g.tenant_id
        ).first()
        if not instructor or str(candidate.instructor_id) != str(instructor.id):
            raise Forbidden('Not authorized to view this candidate')

    query = TheoryHourSession.query.filter_by(
        candidate_id=candidate_id, tenant_id=g.tenant_id
    ).order_by(TheoryHourSession.session_number)

    sessions = query.all()

    rows = []
    for s in sessions:
        rows.append({
            'session_number': s.session_number,
            'date_realized': s.date_realized,
            'time_from': s.time_from.strftime('%H:%M') if s.time_from else '',
            'time_to': s.time_to.strftime('%H:%M') if s.time_to else '',
            'hours_count': s.hours_count,
            'is_realized': s.is_realized,
        })

    columns = [
        ExportColumn(key='session_number', header='Nr. Sesionit', width=14),
        ExportColumn(key='date_realized', header='Data', width=14, formatter=format_date),
        ExportColumn(key='time_from', header='Ora Fillimit', width=14),
        ExportColumn(key='time_to', header='Ora P\u00ebrfundimit', width=16),
        ExportColumn(key='hours_count', header='Nr. Or\u00ebve', width=12),
        ExportColumn(key='is_realized', header='E Realizuar', width=12, formatter=format_boolean),
    ]

    filename = f'ore_teorike_{candidate.first_name}_{candidate.last_name}'
    return _build_export(rows, columns, filename, fmt, sheet_name='Or\u00eb Teorike')


# ==================== PRACTICAL HOURS EXPORT ====================

@api_bp.get('/export/practical-hours')
def export_practical_hours():
    """Export practical hour sessions to Excel/CSV."""
    fmt = _get_format()

    candidate_id = request.args.get('candidateId')
    if not candidate_id:
        raise ValidationError('candidateId is required')

    # Verify candidate belongs to tenant
    candidate = Candidate.query.filter_by(
        id=candidate_id, tenant_id=g.tenant_id, deleted_at=None
    ).first()
    if not candidate:
        raise NotFound('Candidate not found')

    # If instructor role, verify candidate is assigned to them
    if g.current_user.get('role') == 'instructor':
        instructor = Instructor.query.filter_by(
            user_id=g.current_user['sub'], tenant_id=g.tenant_id
        ).first()
        if not instructor or str(candidate.instructor_id) != str(instructor.id):
            raise Forbidden('Not authorized to view this candidate')

    query = PracticalHourSession.query.filter_by(
        candidate_id=candidate_id, tenant_id=g.tenant_id
    ).order_by(PracticalHourSession.date_realized.desc())

    sessions = query.all()

    rows = []
    for s in sessions:
        rows.append({
            'date_realized': s.date_realized,
            'hours_count': s.hours_count,
            'price_per_hour': float(s.price_per_hour) if s.price_per_hour else 0,
            'total_price': s.total_price,
            'chapter_topics': s.chapter_topics or '',
            'instructor': s.instructor.full_name if s.instructor else '',
            'remarks': s.remarks or '',
        })

    columns = [
        ExportColumn(key='date_realized', header='Data', width=14, formatter=format_date),
        ExportColumn(key='hours_count', header='Nr. Or\u00ebve', width=12),
        ExportColumn(key='price_per_hour', header='\u00c7mimi/Or\u00eb (\u20ac)', width=16, formatter=format_currency),
        ExportColumn(key='total_price', header='Totali (\u20ac)', width=14, formatter=format_currency),
        ExportColumn(key='chapter_topics', header='Kapitujt', width=25),
        ExportColumn(key='instructor', header='Instruktori', width=22),
        ExportColumn(key='remarks', header='V\u00ebrejtje', width=30),
    ]

    filename = f'ore_praktike_{candidate.first_name}_{candidate.last_name}'
    return _build_export(rows, columns, filename, fmt, sheet_name='Or\u00eb Praktike')


# ==================== EXAMS EXPORT ====================

@api_bp.get('/export/exams')
def export_exams():
    """Export exams list to Excel/CSV."""
    fmt = _get_format()

    query = Exam.query.filter_by(tenant_id=g.tenant_id)

    candidate_id = request.args.get('candidateId')
    if candidate_id:
        query = query.filter_by(candidate_id=candidate_id)

    exam_type = request.args.get('examType')
    if exam_type:
        query = query.filter_by(exam_type=exam_type)

    result_filter = request.args.get('result')
    if result_filter:
        query = query.filter_by(result=result_filter)

    date_from = request.args.get('dateFrom')
    if date_from:
        try:
            query = query.filter(Exam.exam_date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        except ValueError:
            pass

    date_to = request.args.get('dateTo')
    if date_to:
        try:
            query = query.filter(Exam.exam_date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        except ValueError:
            pass

    exams = query.order_by(Exam.exam_date.desc()).all()

    result_labels = {'scheduled': 'E planifikuar', 'passed': 'Kaluar', 'failed': 'D\u00ebshtuar', 'cancelled': 'Anuluar'}
    type_labels = {'theory': 'Teorik', 'practical': 'Praktik'}

    rows = []
    for e in exams:
        rows.append({
            'candidate': f"{e.candidate.first_name} {e.candidate.last_name}" if e.candidate else '',
            'exam_type': type_labels.get(e.exam_type, e.exam_type),
            'exam_date': e.exam_date,
            'attempt': e.attempt_number,
            'score': e.score or '',
            'result': result_labels.get(e.result, e.result),
            'examiner': e.examiner_name or '',
            'location': e.exam_location or '',
            'notes': e.notes or '',
        })

    columns = [
        ExportColumn(key='candidate', header='Kandidati', width=25),
        ExportColumn(key='exam_type', header='Lloji i Provimit', width=18),
        ExportColumn(key='exam_date', header='Data', width=14, formatter=format_date),
        ExportColumn(key='attempt', header='Tentativa', width=12),
        ExportColumn(key='score', header='Pik\u00ebt', width=10),
        ExportColumn(key='result', header='Rezultati', width=14),
        ExportColumn(key='examiner', header='Ekzaminuesi', width=22),
        ExportColumn(key='location', header='Vendi', width=20),
        ExportColumn(key='notes', header='Sh\u00ebnime', width=30),
    ]

    return _build_export(rows, columns, 'provimet', fmt, sheet_name='Provimet')
