from django.conf import settings
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from .models import User

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
    """May be unnecessary verification, but setting this up for possible future use"""
    
    def decorator(view_function):
        def modified_view_function(request):
            if request.user.category == type:
                return view_function(request)
            else:
                raise PermissionDenied
        return modified_view_function
    return decorator

def admin_dashboard_context():
    total_students = User.objects.filter(user_type='Student').count()
    total_tutors = User.objects.filter(user_type='Tutor').count()
    return {
        'total_students': total_students,
        'total_tutors': total_tutors,
    }

def return_total_students():
    return User.objects.filter(user_type='Student').count()

def return_total_tutors():
    return User.objects.filter(user_type='Tutor').count()