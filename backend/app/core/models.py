"""Import all mapped classes before Alembic inspects metadata."""

from app.users.models import Role, User, user_role  # noqa: F401
from app.subjects.models import Subject  # noqa: F401
from app.periods.models import AcademicPeriod  # noqa: F401
from app.enrollments.models import Enrollment  # noqa: F401
from app.grades.models import Grade  # noqa: F401
