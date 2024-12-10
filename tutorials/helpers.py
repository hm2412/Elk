from django.conf import settings
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from .models import User, Lesson

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