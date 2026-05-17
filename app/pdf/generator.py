"""PDF generation service using WeasyPrint + Jinja2."""
import os
from datetime import date, datetime
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
from flask import g

from app.utils.db import db
from app.models.tenant_model import Tenant
from app.models.candidate_model import Candidate
from app.models.category_model import Category
from app.models.payment_model import Payment
from app.models.theory_hour_session_model import TheoryHourSession
from app.models.practical_hour_session_model import PracticalHourSession
from app.models.verification_model import Verification
from app.middleware.error_handler import NotFound

# Directories
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_TEMPLATE_DIR = os.path.join(_BASE_DIR, 'templates')
_STYLE_DIR = os.path.join(_BASE_DIR, 'styles')
_ASSET_DIR = os.path.join(_BASE_DIR, 'assets')


def _format_date(value) -> str:
    """Format a date as dd.MM.yyyy."""
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    return value.strftime('%d.%m.%Y')


def _format_currency(value) -> str:
    """Format a number as currency with 2 decimals."""
    if value is None:
        return '0.00'
    return f'{float(value):.2f}'


def _safe(value, default: str = '') -> str:
    """Return default if value is None."""
    return value if value is not None else default


class PDFGenerator:
    """Generate PDF documents for the driving school system."""

    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(_TEMPLATE_DIR),
            autoescape=True,
        )
        self.env.filters['format_date'] = _format_date
        self.env.filters['format_currency'] = _format_currency
        self.env.filters['safe_str'] = _safe
        self._css = self._load_css()

    def _load_css(self) -> str:
        css_path = os.path.join(_STYLE_DIR, 'pdf_base.css')
        if os.path.exists(css_path):
            with open(css_path) as f:
                return f.read()
        return ''

    def _get_candidate(self, candidate_id: str) -> Candidate:
        candidate = Candidate.query.filter_by(
            id=candidate_id, tenant_id=g.tenant_id, deleted_at=None
        ).first()
        if not candidate:
            raise NotFound('Candidate not found')
        return candidate

    def _get_tenant(self) -> Tenant:
        return db.session.get(Tenant, g.tenant_id)

    def _render_pdf(self, template_name: str, context: dict, landscape: bool = False) -> bytes:
        template = self.env.get_template(template_name)
        context['asset_dir'] = _ASSET_DIR
        html_content = template.render(**context)
        # Templates include inline CSS; base CSS provides fallback @page rules
        css_text = self._css
        if landscape:
            css_text += '\n@page { size: A4 landscape; margin: 8mm; }'
        html = HTML(string=html_content, base_url=_BASE_DIR)
        css = CSS(string=css_text)
        return html.write_pdf(stylesheets=[css])

    # ----- Document generators -----

    def generate_fatura(self, candidate_id: str) -> bytes:
        """Generate invoice (Fatura) PDF."""
        candidate = self._get_candidate(candidate_id)
        tenant = self._get_tenant()
        category = candidate.category

        price = float(candidate.price) if candidate.price else 0
        vat_rate = 0.18
        price_no_vat = round(price / (1 + vat_rate), 2)
        vat_amount = round(price - price_no_vat, 2)

        payments = Payment.query.filter_by(
            candidate_id=candidate_id, tenant_id=str(g.tenant_id)
        ).order_by(Payment.payment_date).all()
        total_paid = sum(float(p.amount) for p in payments)

        invoice_number = f'{candidate.protocol_number or str(candidate.id)[:8]}/{date.today().year}'

        return self._render_pdf('fatura.html', {
            'tenant': tenant,
            'candidate': candidate,
            'category': category,
            'payments': payments,
            'invoice_number': invoice_number,
            'invoice_date': date.today(),
            'price': price,
            'price_no_vat': price_no_vat,
            'vat_amount': vat_amount,
            'total_paid': total_paid,
            'remaining': price - total_paid,
        })

    def generate_fatura_per_payment(self, candidate_id: str, payment_id: str) -> bytes:
        """Generate invoice (Fatura) PDF for a specific payment, showing debt."""
        candidate = self._get_candidate(candidate_id)
        tenant = self._get_tenant()
        category = candidate.category

        payment = Payment.query.filter_by(
            id=payment_id, candidate_id=candidate_id, tenant_id=str(g.tenant_id)
        ).first()
        if not payment:
            raise NotFound('Payment not found')

        payment_amount = float(payment.amount)
        vat_rate = 0.18
        payment_no_vat = round(payment_amount / (1 + vat_rate), 2)
        payment_vat = round(payment_amount - payment_no_vat, 2)

        all_payments = Payment.query.filter_by(
            candidate_id=candidate_id, tenant_id=str(g.tenant_id)
        ).order_by(Payment.payment_date, Payment.created_at).all()

        total_paid_up_to = 0.0
        payment_sequence = 0
        for idx, p in enumerate(all_payments, 1):
            total_paid_up_to += float(p.amount)
            if str(p.id) == str(payment_id):
                payment_sequence = idx
                break

        total_price = float(candidate.price) if candidate.price else 0
        remaining = total_price - total_paid_up_to

        invoice_number = f'{candidate.protocol_number or str(candidate.id)[:8]}/{payment_sequence}/{date.today().year}'

        return self._render_pdf('fatura.html', {
            'tenant': tenant,
            'candidate': candidate,
            'category': category,
            'invoice_number': invoice_number,
            'invoice_date': payment.payment_date or date.today(),
            'price': payment_amount,
            'price_no_vat': payment_no_vat,
            'vat_amount': payment_vat,
            'total_paid': total_paid_up_to,
            'remaining': remaining,
        })

    def generate_fleteparaqitja(self, candidate_id: str) -> bytes:
        """Generate registration form (Fletëparaqitja) PDF."""
        candidate = self._get_candidate(candidate_id)
        tenant = self._get_tenant()
        category = candidate.category

        all_categories = Category.query.filter_by(
            tenant_id=g.tenant_id, is_active=True
        ).order_by(Category.code).all()

        return self._render_pdf('fleteparaqitja.html', {
            'tenant': tenant,
            'candidate': candidate,
            'category': category,
            'all_categories': all_categories,
            'today': date.today(),
        })

    def generate_libreza(self, candidate_id: str) -> bytes:
        """Generate logbook (Libreza) PDF."""
        candidate = self._get_candidate(candidate_id)
        tenant = self._get_tenant()
        category = candidate.category

        theory_sessions = TheoryHourSession.query.filter_by(
            candidate_id=candidate_id, tenant_id=str(g.tenant_id)
        ).order_by(TheoryHourSession.session_number).all()

        practical_sessions = PracticalHourSession.query.filter_by(
            candidate_id=candidate_id, tenant_id=str(g.tenant_id)
        ).order_by(PracticalHourSession.date_realized).all()

        return self._render_pdf('libreza.html', {
            'tenant': tenant,
            'candidate': candidate,
            'category': category,
            'theory_sessions': theory_sessions,
            'practical_sessions': practical_sessions,
            'today': date.today(),
        }, landscape=True)

    def generate_kontrata(self, candidate_id: str) -> bytes:
        """Generate contract (Kontrata) PDF."""
        candidate = self._get_candidate(candidate_id)
        tenant = self._get_tenant()
        category = candidate.category

        residence_parts = []
        if candidate.residence_place:
            residence_parts.append(candidate.residence_place.name)
        if candidate.residence_municipality:
            residence_parts.append(candidate.residence_municipality.name)
        candidate_residence = ', '.join(residence_parts) if residence_parts else '___________'

        return self._render_pdf('kontrata.html', {
            'tenant': tenant,
            'candidate': candidate,
            'category': category,
            'candidate_residence': candidate_residence,
            'contract_date': candidate.registration_date or date.today(),
            'today': date.today(),
        })

    def generate_testi(self, candidate_id: str, questions: list = None) -> bytes:
        """Generate test result (Testi) PDF.

        Args:
            candidate_id: UUID of the candidate.
            questions: Optional list of question dicts, each with:
                - number: int (question number)
                - text: str (question text)
                - image: str or None (absolute path to traffic sign image)
                - points: int (points for this question)
                - answers: list of dicts, each with:
                    - label: str ('A', 'B', or 'C')
                    - text: str (answer text)
                    - is_correct: bool
                    - is_selected: bool
        """
        candidate = self._get_candidate(candidate_id)
        tenant = self._get_tenant()
        category = candidate.category

        return self._render_pdf('testi.html', {
            'tenant': tenant,
            'candidate': candidate,
            'category': category,
            'questions': questions or [],
            'today': date.today(),
        })

    def generate_certificate(self, candidate_id: str) -> bytes:
        """Generate verification certificate (Vërtetimi) PDF."""
        candidate = self._get_candidate(candidate_id)
        tenant = self._get_tenant()
        category = candidate.category

        theory_sessions = TheoryHourSession.query.filter_by(
            candidate_id=candidate_id, tenant_id=str(g.tenant_id), is_realized=True
        ).all()
        practical_sessions = PracticalHourSession.query.filter_by(
            candidate_id=candidate_id, tenant_id=str(g.tenant_id)
        ).all()

        theory_hours_total = sum(s.hours_count for s in theory_sessions)
        practical_hours_total = sum(s.hours_count for s in practical_sessions)

        verification = Verification.query.filter_by(
            candidate_id=candidate_id, tenant_id=str(g.tenant_id)
        ).first()

        return self._render_pdf('vertetimi.html', {
            'tenant': tenant,
            'candidate': candidate,
            'category': category,
            'verification': verification,
            'theory_hours_total': theory_hours_total,
            'practical_hours_total': practical_hours_total,
            'today': date.today(),
        })

    def generate_candidate_list(self, filters: dict) -> bytes:
        """Generate candidate list PDF."""
        tenant = self._get_tenant()

        query = Candidate.query.filter_by(
            tenant_id=g.tenant_id, deleted_at=None
        )

        if filters.get('category_id'):
            query = query.filter_by(category_id=filters['category_id'])
        if filters.get('instructor_id'):
            query = query.filter_by(instructor_id=filters['instructor_id'])
        if filters.get('archived') != 'true':
            query = query.filter_by(is_archived=False)
        if filters.get('from_date'):
            query = query.filter(Candidate.registration_date >= filters['from_date'])
        if filters.get('to_date'):
            query = query.filter(Candidate.registration_date <= filters['to_date'])

        candidates = query.order_by(Candidate.registration_date, Candidate.last_name).all()

        return self._render_pdf('candidate_list.html', {
            'tenant': tenant,
            'candidates': candidates,
            'filters': filters,
            'today': date.today(),
            'total_count': len(candidates),
        })
