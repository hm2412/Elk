from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from tutorials.models import User, Lesson, Meeting
from tutorials.forms import MeetingForm

from tutorials.helpers import (
    user_role_required, 
    get_lesson_times,
    delete_lesson_request
)

@login_required
@user_role_required('Admin')
def schedule_session(request, student_id):
    """Display a form to schedule tutoring sessions"""
    student = get_object_or_404(User, id=student_id, user_type='Student')
    lesson_request = Lesson.objects.filter(student=student).first()

    lesson_start_time, lesson_end_time = get_lesson_times(lesson_request)

    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.student = student
            meeting.save()

            delete_lesson_request(lesson_request)

            return redirect('dashboard')  # Redirect to the admin dashboard
    else:
        form = MeetingForm(initial={'student': student, 
                                    'start_time': lesson_start_time, 
                                    'end_time': lesson_end_time,})

    return render(request, 'admin/schedule_session.html', {'form': form, 'student': student, 'request': lesson_request})