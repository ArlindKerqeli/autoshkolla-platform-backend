from flask import request, g, make_response
from app.api import api_bp
from app.pdf.generator import PDFGenerator


def _pdf_response(pdf_bytes: bytes, filename: str):
    """Create a Flask response with PDF content."""
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


@api_bp.get('/print/invoice/<candidate_id>')
def print_invoice(candidate_id):
    """Generate invoice PDF (Fatura) for a candidate."""
    gen = PDFGenerator()
    pdf = gen.generate_fatura(candidate_id)
    return _pdf_response(pdf, f'fatura-{candidate_id[:8]}.pdf')


@api_bp.get('/print/invoice/<candidate_id>/payment/<payment_id>')
def print_payment_invoice(candidate_id, payment_id):
    """Generate invoice PDF (Fatura) for a specific payment."""
    gen = PDFGenerator()
    pdf = gen.generate_fatura_per_payment(candidate_id, payment_id)
    return _pdf_response(pdf, f'fatura-{candidate_id[:8]}-{payment_id[:8]}.pdf')


@api_bp.get('/print/registration-form/<candidate_id>')
def print_registration_form(candidate_id):
    """Generate registration form PDF (Fletëparaqitja) for a candidate."""
    gen = PDFGenerator()
    pdf = gen.generate_fleteparaqitja(candidate_id)
    return _pdf_response(pdf, f'fleteparaqitja-{candidate_id[:8]}.pdf')


@api_bp.get('/print/logbook/<candidate_id>')
def print_logbook(candidate_id):
    """Generate logbook PDF (Libreza) for a candidate."""
    gen = PDFGenerator()
    pdf = gen.generate_libreza(candidate_id)
    return _pdf_response(pdf, f'libreza-{candidate_id[:8]}.pdf')


@api_bp.get('/print/contract/<candidate_id>')
def print_contract(candidate_id):
    """Generate contract PDF (Kontrata) for a candidate."""
    gen = PDFGenerator()
    pdf = gen.generate_kontrata(candidate_id)
    return _pdf_response(pdf, f'kontrata-{candidate_id[:8]}.pdf')


@api_bp.get('/print/test-result/<candidate_id>')
def print_test_result(candidate_id):
    """Generate test result PDF (Testi) for a candidate."""
    gen = PDFGenerator()
    pdf = gen.generate_testi(candidate_id)
    return _pdf_response(pdf, f'testi-{candidate_id[:8]}.pdf')


@api_bp.get('/print/certificate/<candidate_id>')
def print_certificate(candidate_id):
    """Generate certificate PDF (Vërtetimi) for a candidate."""
    gen = PDFGenerator()
    pdf = gen.generate_certificate(candidate_id)
    return _pdf_response(pdf, f'vertetimi-{candidate_id[:8]}.pdf')


@api_bp.get('/print/candidate-list')
def print_candidate_list():
    """Generate candidate list PDF with filtering support."""
    filters = {
        'category_id': request.args.get('category_id'),
        'instructor_id': request.args.get('instructor_id'),
        'archived': request.args.get('archived'),
        'from_date': request.args.get('from_date'),
        'to_date': request.args.get('to_date'),
    }
    gen = PDFGenerator()
    pdf = gen.generate_candidate_list(filters)
    return _pdf_response(pdf, 'kandidatet-lista.pdf')
