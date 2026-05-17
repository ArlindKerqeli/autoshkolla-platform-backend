from flask import Blueprint

api_bp = Blueprint('api', __name__)

from app.api import health  # noqa: E402, F401
from app.api import auth  # noqa: E402, F401
from app.api import locations  # noqa: E402, F401
from app.api import school  # noqa: E402, F401
from app.api import categories  # noqa: E402, F401
from app.api import instructors  # noqa: E402, F401
from app.api import vehicles  # noqa: E402, F401

from app.api import candidates  # noqa: E402, F401
from app.api import scheduled_lessons  # noqa: E402, F401
from app.api import messages  # noqa: E402, F401
from app.api import instructor_portal  # noqa: E402, F401
from app.api import dashboard  # noqa: E402, F401
from app.api import instructor_payments  # noqa: E402, F401

from app.api import lesson_chapters  # noqa: E402, F401
from app.api import theory_hours  # noqa: E402, F401
from app.api import practical_hours  # noqa: E402, F401
from app.api import payments  # noqa: E402, F401
from app.api import verifications  # noqa: E402, F401
from app.api import expenses  # noqa: E402, F401
from app.api import users  # noqa: E402, F401
from app.api import superadmin  # noqa: E402, F401
from app.api import print_docs  # noqa: E402, F401
from app.api import exams  # noqa: E402, F401
from app.api import exports  # noqa: E402, F401
