# standard imports
from datetime import datetime, time, timedelta
import json

# django imports
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, UpdateView

from .models import (
    User, 
    Lesson, 
    Meeting, 
    TutorProfile, 
    TutorAvailability
)
from .forms import (
    LogInForm, 
    PasswordForm, 
    UserForm, 
    SignUpForm, 
    MeetingForm, 
    LessonRequestForm,
    TutorAvailabilityForm,
    TutorHourlyRateForm,
    TutorSubjectsForm
)
from .helpers import (
    login_prohibited, 
    admin_dashboard_context, 
    tutor_dashboard_context, 
    user_role_required, 
    get_meetings_sorted,
    get_lesson_times,
    delete_lesson_request
)

from .helpers import (
    handle_students_list,
    handle_tutors_list,
    handle_invalid_or_forbidden_list,
    paginate_users,
    render_user_list
)

from .calendar_utils import (
    TutorCalendar
)

# Dashboard views
from django.urls import reverse_lazy
from django.http import JsonResponse
import json
from .calendar_utils import TutorCalendar
from .forms import LessonRequestForm
from .forms import Review
from .forms import ReviewForm


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
        
        # Add debug prints
        print("=== Tutor Profile Debug Info ===")
        print(f"Hourly Rate: {tutor_profile.hourly_rate}")
        print(f"Subjects: {tutor_profile.subjects}")
        
        availability_slots = TutorAvailability.objects.filter(tutor=request.user)

        # More debug prints
        print("\n=== Availability Slots ===")
        for slot in availability_slots:
            print(f"{slot.day}: {slot.start_time} - {slot.end_time}")
        print("============================")
        print("\n=== Meetings ===")
        for meeting in meetings:
            print(f"Meeting on {meeting.date}: {meeting.start_time}-{meeting.end_time}")
        print("============================")

        calendar = TutorCalendar(year, month)
        calendar_data = calendar.get_calendar_data(
            meetings=meetings,
            availability_slots=availability_slots
        )

        # Debug calendar data
        print("\nCalendar Data:")
        for week in calendar_data['weeks']:
            for day in week:
                if day['meetings']:
                    print(f"Day {day['day']} has meetings:")
                    for meeting in day['meetings']:
                        print(f"- {meeting['start']} - {meeting['end']}: {meeting['topic']}")
        
        print("==================")

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


from django.shortcuts import render
from .models import Review

@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')

# Sign up/log in handling

class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url


class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')


class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('dashboard')
    
class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

# Profile handling

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

# Tutor dashboard view functions

@login_required
def tutor_availability(request):
    if request.method == 'POST':
        # Clear existing availability
        TutorAvailability.objects.filter(tutor=request.user).delete()
        
        # Process each day
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            if request.POST.get(f'{day}_enabled'):
                start_time = request.POST.get(f'{day}_start_time')
                end_time = request.POST.get(f'{day}_end_time')
                
                if start_time and end_time:
                    TutorAvailability.objects.create(
                        tutor=request.user,
                        day=day.capitalize(),
                        start_time=start_time,
                        end_time=end_time,
                        is_available=True
                    )
        
        messages.success(request, 'Availability updated successfully')
        return redirect('dashboard')
    
    return redirect('dashboard')


@login_required
def tutor_hourly_rate(request):
    if request.method == 'POST':
        hourly_rate = request.POST.get('hourly_rate')
        if hourly_rate:
            tutor_profile, _ = TutorProfile.objects.get_or_create(tutor=request.user)
            tutor_profile.hourly_rate = hourly_rate
            tutor_profile.save()
            messages.success(request, 'Hourly rate updated successfully')
        
        return redirect('dashboard')
    
    return redirect('dashboard')


@login_required
def tutor_subjects(request):
    if request.method == 'POST':
        subjects = request.POST.getlist('subjects')
        tutor_profile, _ = TutorProfile.objects.get_or_create(tutor=request.user)
        tutor_profile.subjects = subjects
        tutor_profile.save()
        messages.success(request, 'Teaching subjects updated successfully')
        return redirect('dashboard')
    
    return redirect('dashboard')


@login_required
@require_http_methods(["POST"])
def set_hourly_rate(request):
    """Set tutor's hourly rate."""
    if request.user.user_type != 'Tutor':
        return JsonResponse({'success': False, 'error': 'User is not a tutor'}, status=403)
    
    try:
        data = json.loads(request.body)
        hourly_rate = data.get('hourly_rate')
        
        tutor_profile, created = TutorProfile.objects.get_or_create(tutor=request.user)
        tutor_profile.hourly_rate = hourly_rate
        tutor_profile.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def set_subjects(request):
    """Set tutor's teaching subjects."""
    if request.user.user_type != 'Tutor':
        return JsonResponse({'success': False, 'error': 'User is not a tutor'}, status=403)
    
    try:
        data = json.loads(request.body)
        subjects = data.get('subjects', [])
        
        tutor_profile, created = TutorProfile.objects.get_or_create(tutor=request.user)
        tutor_profile.subjects = subjects
        tutor_profile.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def set_availability(request):
    """Set tutor's weekly availability."""
    if request.user.user_type != 'Tutor':
        return JsonResponse({'success': False, 'error': 'User is not a tutor'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        # Clear existing availability for this tutor
        TutorAvailability.objects.filter(tutor=request.user).delete()
        
        # Create new availability slots
        for day, slots in data.items():
            if day.endswith('_enabled') and data[day]:  # If day is enabled
                day_name = day.replace('_enabled', '')
                time_slots = data.get(f"{day_name}_slots", [])
                
                for slot in time_slots:
                    TutorAvailability.objects.create(
                        tutor=request.user,
                        day=day_name.capitalize(),
                        start_time=slot['start_time'],
                        end_time=slot['end_time'],
                        is_available=True
                    )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
# Student dashboard view functions
@login_required
def create_lesson_request(request):
    if request.method == 'POST':
        form = LessonRequestForm(request.POST)
        if form.is_valid():
            lesson_request = form.save(commit=False)
            lesson_request.student = request.user 
            lesson_request.save()  
            return redirect('dashboard')  
    else:
        form = LessonRequestForm()

    return render(request, 'lesson_request.html', {'form': form})

@login_required
def view_lesson_request(request):
    lesson = Lesson.objects.filter(student=request.user).first()
    
    lesson_requests = Lesson.objects.filter(student=request.user).order_by('id')
    paginator = Paginator(lesson_requests, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'view_lesson_request.html', {
        'lesson': lesson,
        'lesson_requests': page_obj
    })

class TutorAvailabilityView(LoginRequiredMixin, TemplateView):
    template_name = 'tutor/availability.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['availability_slots'] = TutorAvailability.objects.filter(tutor=self.request.user)
        context['form'] = TutorAvailabilityForm()
        return context

class AddAvailabilitySlotView(LoginRequiredMixin, FormView):
    form_class = TutorAvailabilityForm
    success_url = reverse_lazy('tutor_availability')
    
    def form_valid(self, form):
        TutorAvailability.objects.create(
            tutor=self.request.user,
            day=form.cleaned_data['day'],
            start_time=form.cleaned_data['start_time'],
            end_time=form.cleaned_data['end_time']
        )
        messages.success(self.request, 'Availability slot added successfully.')
        return super().form_valid(form)

class DeleteAvailabilitySlotView(LoginRequiredMixin, View):
    def post(self, request, slot_id):
        slot = get_object_or_404(TutorAvailability, id=slot_id, tutor=request.user)
        slot.delete()
        messages.success(request, 'Availability slot deleted.')
        return redirect('tutor_availability')

class TutorHourlyRateView(LoginRequiredMixin, FormView):
    template_name = 'tutor/hourly_rate.html'
    form_class = TutorHourlyRateForm
    success_url = reverse_lazy('dashboard')
    
    def get_initial(self):
        profile, _ = TutorProfile.objects.get_or_create(tutor=self.request.user)
        return {'hourly_rate': profile.hourly_rate}
    
    def form_valid(self, form):
        profile, _ = TutorProfile.objects.get_or_create(tutor=self.request.user)
        profile.hourly_rate = form.cleaned_data['hourly_rate']
        profile.save()
        messages.success(self.request, 'Hourly rate updated successfully.')
        return super().form_valid(form)

class TutorSubjectsForm(forms.Form):
    SUBJECT_CHOICES = [
        ('Ruby', 'Ruby'),
        ('Swift', 'Swift'),
        ('Scala', 'Scala'),
        ('Java', 'Java'),
        ('Javascript/React', 'Javascript/React'),
        ('Python/Tensorflow', 'Python/Tensorflow'),
        ('C++', 'C++'),
        ('C#', 'C#'),
    ]
    subjects = forms.MultipleChoiceField(
        choices=SUBJECT_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )

class TutorSubjectsView(LoginRequiredMixin, FormView):
    template_name = 'tutor/subjects.html'
    form_class = TutorSubjectsForm
    success_url = reverse_lazy('dashboard')
    
    def get_initial(self):
        profile, _ = TutorProfile.objects.get_or_create(tutor=self.request.user)
        return {'subjects': profile.subjects}
    
    def form_valid(self, form):
        profile, _ = TutorProfile.objects.get_or_create(tutor=self.request.user)
        profile.subjects = form.cleaned_data['subjects']
        profile.save()
        messages.success(self.request, 'Teaching subjects updated successfully.')
        return super().form_valid(form)

class AddCustomSubjectView(LoginRequiredMixin, FormView):
    template_name = 'tutor/custom_subject.html'
    form_class = forms.Form
    success_url = reverse_lazy('tutor_subjects')
    
    def get_form(self):
        form = super().get_form()
        form.fields['custom_subject'] = forms.CharField(max_length=100)
        return form
    
    def form_valid(self, form):
        profile, _ = TutorProfile.objects.get_or_create(tutor=self.request.user)
        custom_subject = form.cleaned_data['custom_subject']
        profile.subjects = list(profile.subjects) + [custom_subject]
        profile.save()
        messages.success(self.request, f'Added custom subject: {custom_subject}')
        return super().form_valid(form)

# User list handling

def user_list(request, list_type):
    if request.user.user_type == 'Student':
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

# Admin dashboard view functions

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

from django.contrib import messages  # Import the messages framework
from django.shortcuts import render, redirect
from tutorials.forms import ReviewForm

def submit_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.student = request.user  # Ensure the logged-in user is assigned
            review.save()

            # Add a success message
            messages.success(request, 'Thank you for your feedback!')

            return redirect('submit_review')  # Redirect to the same page to show the message
    else:
        form = ReviewForm()

    return render(request, 'review.html', {
        'review': form, 
        'is_review_page': True  # This will ensure 'review.css' is loaded
    })

@login_required
def save_lesson_notes(request):
    if request.method == 'POST':
        lesson_id = request.POST.get('lesson_id')
        notes = request.POST.get('notes')
        meeting = get_object_or_404(Meeting, id=lesson_id)
        meeting.notes = notes
        meeting.save()
        messages.success(request, 'Notes saved successfully')
        return redirect('dashboard')
    return redirect('dashboard')
