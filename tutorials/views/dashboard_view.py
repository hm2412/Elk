
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from tutorials.models import Meeting, TutorProfile, TutorAvailability

from tutorials.helpers import (
    admin_dashboard_context, 
    tutor_dashboard_context, 
    get_meetings_sorted,
)

from tutorials.calendar_utils import TutorCalendar

@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    user_type = current_user.user_type
    meetings = get_meetings_sorted(current_user)

    context = {
        'user': current_user,
        'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'meetings_sorted': meetings,
    }

    if user_type == 'Tutor':
        context.update(tutor_dashboard_context(request, current_user))
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
            'Computer Programming' : ['Ruby', 'Swift', 'Scala', 'Java', 'Javascript/React', 'Python/Tensorflow', 'C++', 'C#'],
        }

        context.update({
            'tutor_profile': tutor_profile,
            'availability_slots': availability_slots,
            'hourly_rate': tutor_profile.hourly_rate or '',
            'subject_choices': subject_choices,
            'selected_subjects': tutor_profile.subjects,
            'calendar_data': calendar_data,
            'meetings': meetings,
        })
        template = 'tutor/dashboard_tutor.html'
    elif user_type == 'Student':
        template = 'student/dashboard_student.html'
    elif user_type == 'Admin':
        context.update(admin_dashboard_context())
        template = 'admin/dashboard_admin.html'
    else:
        template = 'student/dashboard_student.html'
    
    return render(request, template, context)