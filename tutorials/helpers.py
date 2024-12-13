from django.conf import settings
from django.shortcuts import redirect, render
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from functools import wraps
from datetime import datetime, timedelta, time
from .models import ( 
    User,
    Lesson,
    Meeting, 
    TutorAvailability, 
    TutorProfile
)
from .calendar_utils import TutorCalendar

def login_prohibited(view_function):
    """Decorator for view functions that redirect users away if they are logged in."""
    
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
    return modified_view_function

def user_role_required(roles):
    """
    Decorator to check if user has required role(s).
    Accepts a single role string or a list of roles.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrap(request, *args, **kwargs):
            if isinstance(roles, str):
                allowed_roles = [roles]
            else:
                allowed_roles = roles

            if not request.user.is_authenticated or request.user.user_type not in allowed_roles:
                return HttpResponseForbidden("You do not have permission to access this page.")
            return view_func(request, *args, **kwargs)
        return wrap
    return decorator

def admin_dashboard_context():
    total_students = User.objects.filter(user_type='Student').count()
    total_tutors = User.objects.filter(user_type='Tutor').count()
    '''requests = Request.objects.filter(student__user_type='Student').order_by('-submitted_at')'''
    requests = Lesson.objects.all().order_by('-created_at')
    return {
        'total_students': total_students,
        'total_tutors': total_tutors,
        'requests': requests,
    }

def tutor_dashboard_context(request, current_user):
    tutor_profile, created = TutorProfile.objects.get_or_create(tutor=current_user)
    current_date = datetime.now()
    month = int(request.GET.get('month')) if request.GET.get('month') else current_date.month
    year = int(request.GET.get('year')) if request.GET.get('year') else current_date.year

    meetings = Meeting.objects.filter(
        tutor=current_user, 
        date__year=year,
        date__month=month
    ).select_related('student')

    availability_slots = TutorAvailability.objects.filter(tutor=request.user)

    calendar = TutorCalendar(year, month)
    calendar_data = calendar.get_calendar_data(
        meetings=meetings,
        availability_slots=availability_slots
    )

    subject_choices = {
        'STEM' : ['Mathematics', 'Computer Science', 'Physics', 'Chemistry', 'Biology'],
        'Languages' : ['English', 'Spanish', 'French', 'German'],
        'Humanities' : ['Geography', 'History', 'Philosophy', 'Religious Studies']
    }

    return {
        'tutor_profile': tutor_profile,
        'availability_slots': availability_slots,
        'hourly_rate': tutor_profile.hourly_rate or '',
        'subject_choices': subject_choices,
        'selected_subjects': tutor_profile.subjects,
        'calendar_data': calendar_data,
        'meetings': meetings,
    }

def get_students_for_tutor(tutor):
    meetings = Meeting.objects.filter(tutor=tutor)
    students = meetings.values_list('student', flat=True)
    return User.objects.filter(id__in=students).order_by('username')

def get_all_students():
    return User.objects.filter(user_type='Student').order_by('username')

def annotate_students_with_tutors(users):
    for user in users:
        tutor_usernames = Meeting.objects.filter(student=user, status='scheduled').values_list('tutor__username', flat=True)
        user.current_tutors = list(set(tutor_usernames))

def get_all_tutors():
    return User.objects.filter(user_type='Tutor').order_by('username')

def filter_tutors_by_subjects(users, subject_filters):
    return [
        user for user in users 
        if hasattr(user, 'tutor_profile') and any(subject in subject_filters for subject in user.tutor_profile.subjects)
    ]

def annotate_tutors_with_availability(users):
    availability = TutorAvailability.objects.filter(tutor__in=users).order_by('tutor', 'day', 'start_time')
    for user in users:
        user.availability = availability.filter(tutor=user)

def handle_students_list(request):
    if request.user.user_type == 'Tutor':
        users = get_students_for_tutor(request.user)
        title = "Your Students"
    else:
        users = get_all_students()
        title = "Student List"
    annotate_students_with_tutors(users)
    return users, title

def handle_tutors_list(request):
    filters = {}
    users = get_all_tutors()
    subject_filters = request.GET.getlist('subjects', [])
    if subject_filters:
        users = filter_tutors_by_subjects(users, subject_filters)
        filters['subjects'] = subject_filters
    annotate_tutors_with_availability(users)
    title = "Tutor List"
    return users, title, filters

def handle_invalid_or_forbidden_list(list_type, user_type):
    if list_type not in ['students', 'tutors'] or user_type not in ['Tutor', 'Admin']:
        return [], "Invalid List Type", {}
    return [], "Access Denied", {}

def get_subject_choices():
    from .views import TutorSubjectsForm
    return TutorSubjectsForm.SUBJECT_CHOICES

def paginate_users(request, users, items_per_page=25):
    paginator = Paginator(users, items_per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

def render_user_list(request, users, title, filters):
    return render(request, 'partials/lists.html', {
        'users': users,
        'title': title,
        'filters': filters,
        'subjects': get_subject_choices(),
    })

def get_lesson_times(lesson_request):
    if lesson_request:
        lesson_start_time = lesson_request.start_time
        duration = lesson_request.duration
    else:
        lesson_start_time = time(10, 0)
        duration = 30
    
    start_converted = datetime.combine(datetime.today(), lesson_start_time)
    lesson_end_time = (start_converted + timedelta(minutes=duration)).time()
    
    return lesson_start_time, lesson_end_time

def delete_lesson_request(lesson_request):
    if lesson_request:
        lesson_request.delete()

def get_meetings_sorted(user):
    """Organize lessons by time of day and day of the week."""

    meetings_sorted = {
        'morning': { 'mon': [], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': [] },
        'afternoon': { 'mon': [], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': [] },
        'evening': { 'mon': [], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': [] },
    }

    for meeting in Meeting.objects.filter(student=user):
        time_of_day = meeting.time_of_day
        day = meeting.day
        if time_of_day not in meetings_sorted:
            continue

        if day not in meetings_sorted[time_of_day]:
            continue

        meetings_sorted[time_of_day][day].append(meeting)
    
    return meetings_sorted
