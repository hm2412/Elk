
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from tutorials.helpers import (
    handle_students_list,
    handle_tutors_list,
    handle_invalid_or_forbidden_list,
    paginate_users,
    render_user_list
)

@login_required
def user_list(request, list_type):
    """Handle user list viewing with proper access control"""
    if not request.user.is_authenticated or request.user.user_type == 'Student':
        return HttpResponseForbidden("You do not have permission to access this page.")

    users, title, filters = [], "Invalid List Type", {}

    if list_type == 'students':
        users, title = handle_students_list(request)
    elif list_type == 'tutors' and request.user.user_type == 'Admin':
        users, title, filters = handle_tutors_list(request)
    else:
        users, title, filters = handle_invalid_or_forbidden_list(list_type, request.user.user_type)

    users = paginate_users(request, users)
    return render_user_list(request, users, title, filters)