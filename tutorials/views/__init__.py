from .mixins import LoginProhibitedMixin
from .dashboard_view import dashboard
from .home_view import Home
from .login_views import LogInView, log_out
from .signup_view import SignUpView
from .profile_views import ProfileUpdateView, PasswordView
from .student_views import view_lesson_request, create_lesson_request, submit_review
from .admin_views import schedule_session, save_lesson_notes
from .tutor_views import(
    tutor_availability, 
    tutor_hourly_rate, 
    tutor_subjects, 
    set_hourly_rate, 
    set_availability, 
    set_subjects
)
from .tutor_classes import (
    TutorAvailabilityView, 
    AddAvailabilitySlotView,
    DeleteAvailabilitySlotView,
    TutorHourlyRateView,
    TutorSubjectsForm,
    TutorSubjectsView
)

from .userlist_view import user_list
