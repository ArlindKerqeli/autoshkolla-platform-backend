from datetime import datetime
from app.utils.db import db
from app.models.exam_model import Exam
from app.models.candidate_model import Candidate
from app.models.theory_hour_session_model import TheoryHourSession
from app.middleware.error_handler import ValidationError, NotFound


class ExamService:
    """Business logic for exam tracking."""

    def get_candidate_or_404(self, tenant_id: str, candidate_id: str) -> Candidate:
        """Fetch candidate or raise NotFound."""
        candidate = Candidate.query.filter_by(
            id=candidate_id, tenant_id=tenant_id, deleted_at=None
        ).first()
        if not candidate:
            raise NotFound('Kandidati nuk u gjet')
        return candidate

    def check_eligibility(self, tenant_id: str, candidate_id: str) -> dict:
        """Check whether a candidate is eligible for theory and/or practical exams."""
        candidate = self.get_candidate_or_404(tenant_id, candidate_id)

        # Theory hours check
        theory_realized = TheoryHourSession.query.filter_by(
            candidate_id=candidate_id, tenant_id=tenant_id, is_realized=True
        ).count()
        theory_needed = candidate.theory_hours or 0
        theory_eligible = theory_realized >= theory_needed if theory_needed > 0 else True

        # Check if theory exam already passed
        theory_passed = Exam.query.filter_by(
            candidate_id=candidate_id, tenant_id=tenant_id,
            exam_type='theory', result='passed'
        ).first() is not None

        # Practical hours check
        practical_realized = candidate.practical_hours_realized or 0
        practical_needed = candidate.practical_hours or 0
        practical_hours_ok = practical_realized >= practical_needed if practical_needed > 0 else True
        practical_eligible = theory_passed and practical_hours_ok

        # Build reasons
        theory_reason = 'I plotëson kushtet' if theory_eligible else \
            f'Ka realizuar {theory_realized}/{theory_needed} orë teorike'

        if not theory_passed and not practical_hours_ok:
            practical_reason = (
                f'Provimi teorik nuk është kaluar dhe ka realizuar '
                f'{practical_realized}/{practical_needed} orë praktike'
            )
        elif not theory_passed:
            practical_reason = 'Provimi teorik nuk është kaluar'
        elif not practical_hours_ok:
            practical_reason = f'Ka realizuar {practical_realized}/{practical_needed} orë praktike'
        else:
            practical_reason = 'I plotëson kushtet'

        return {
            'theoryEligible': theory_eligible,
            'theoryReason': theory_reason,
            'practicalEligible': practical_eligible,
            'practicalReason': practical_reason,
            'theoryHoursRealized': theory_realized,
            'theoryHoursNeeded': theory_needed,
            'practicalHoursRealized': practical_realized,
            'practicalHoursNeeded': practical_needed,
            'theoryExamPassed': theory_passed,
        }

    def calculate_attempt_number(self, tenant_id: str, candidate_id: str, exam_type: str) -> int:
        """Calculate the next attempt number for a candidate's exam type."""
        count = Exam.query.filter_by(
            tenant_id=tenant_id, candidate_id=candidate_id, exam_type=exam_type
        ).count()
        return count + 1

    def create_exam(self, tenant_id: str, data: dict) -> Exam:
        """Create a new exam record with eligibility validation."""
        self.get_candidate_or_404(tenant_id, data['candidateId'])

        # Check eligibility
        eligibility = self.check_eligibility(tenant_id, data['candidateId'])
        if data['examType'] == 'theory' and not eligibility['theoryEligible']:
            raise ValidationError(
                f"Kandidati nuk i plotëson kushtet për provimin teorik: {eligibility['theoryReason']}"
            )
        if data['examType'] == 'practical' and not eligibility['practicalEligible']:
            raise ValidationError(
                f"Kandidati nuk i plotëson kushtet për provimin praktik: {eligibility['practicalReason']}"
            )

        attempt = self.calculate_attempt_number(tenant_id, data['candidateId'], data['examType'])

        exam_date = None
        if data.get('examDate'):
            try:
                exam_date = datetime.strptime(data['examDate'], '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError('Formati i datës nuk është i vlefshëm (YYYY-MM-DD)')

        exam = Exam(
            tenant_id=tenant_id,
            candidate_id=data['candidateId'],
            exam_type=data['examType'],
            exam_date=exam_date,
            score=data.get('score'),
            result=data.get('result', 'scheduled'),
            attempt_number=attempt,
            notes=data.get('notes'),
            examiner_name=data.get('examinerName'),
            exam_location=data.get('examLocation'),
        )
        db.session.add(exam)
        db.session.commit()
        return exam

    def update_exam(self, tenant_id: str, exam_id: str, data: dict) -> Exam:
        """Update an existing exam record."""
        exam = Exam.query.filter_by(id=exam_id, tenant_id=tenant_id).first()
        if not exam:
            raise NotFound('Provimi nuk u gjet')

        if 'examDate' in data and data['examDate']:
            try:
                exam.exam_date = datetime.strptime(data['examDate'], '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError('Formati i datës nuk është i vlefshëm')
        if 'score' in data:
            exam.score = data['score']
        if 'result' in data:
            exam.result = data['result']
        if 'notes' in data:
            exam.notes = data['notes']
        if 'examinerName' in data:
            exam.examiner_name = data['examinerName']
        if 'examLocation' in data:
            exam.exam_location = data['examLocation']

        db.session.commit()
        return exam

    def delete_exam(self, tenant_id: str, exam_id: str) -> None:
        """Hard-delete an exam record."""
        exam = Exam.query.filter_by(id=exam_id, tenant_id=tenant_id).first()
        if not exam:
            raise NotFound('Provimi nuk u gjet')
        db.session.delete(exam)
        db.session.commit()


exam_service = ExamService()
