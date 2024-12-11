from django.conf import settings
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from .models import User, Lesson
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import User, Meeting, TutorAvailability

def login_prohibited(view_function):
    """Decorator for view functions that redirect users away if they are logged in."""
    
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
    return modified_view_function

def user_role_required(type):
    """Decorator for view functions that denies permission if they are not the specified type"""
    
    def decorator(view_function):
        def modified_view_function(request, *args, **kwargs):
            if request.user.user_type == type:
                return view_function(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return modified_view_function
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




def get_students_for_tutor(tutor):
    meetings = Meeting.objects.filter(tutor=tutor)
    students = meetings.values_list('student', flat=True)
    return User.objects.filter(id__in=students).order_by('username')

def get_all_students():
    return User.objects.filter(user_type='Student').order_by('username')

def annotate_students_with_tutors(users):
    for user in users:
        user.current_tutors = Meeting.objects.filter(student=user, status='scheduled').values_list('tutor__username', flat=True)

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