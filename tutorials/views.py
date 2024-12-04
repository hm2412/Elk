from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited

@login_required

def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    lessons = get_lessons_sorted(current_user)

    context = {
        'user': current_user,
        'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'lessons_time_and_day': lessons,
    }

    print("current user is: " + current_user.user_type)

    user_type = current_user.user_type

    if user_type == 'Tutor':
        template = 'tutor/dashboard_tutor.html'
    elif user_type == 'student':
        template = 'student/dashboard_student.html'
    elif user_type == 'Admin':
        template = 'admin/dashboard_admin.html'
    else:
        template = 'student/dashboard_student.html'
    
    # return render(request, template, {'user': current_user})
    return render(request, template, context)


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')

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
    
""" Views for Student Dashboard below"""

from .forms import LessonRequestForm
from .models import Lesson

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

def view_lesson_request(request):
    lesson_request = Lesson.objects.filter(student=request.user)
    return render(request, 'view_lesson_request.html', {'lesson_requests': lesson_request})

def get_lessons_sorted(user):
    """Organize lessons by time of day and day of the week."""
    lessons = Lesson.objects.filter(student=user)

    lessons_by_time_and_day = {
        'morning': { 'mon': [], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': [] },
        'afternoon': { 'mon': [], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': [] },
        'evening': { 'mon': [], 'tue': [], 'wed': [], 'thu': [], 'fri': [], 'sat': [], 'sun': [] },
    }

    for lesson in lessons:
        for day in lesson.days:
            if lesson.time_of_day in lessons_by_time_and_day:
                lessons_by_time_and_day[lesson.time_of_day][day].append(lesson)
    
    return lessons_by_time_and_day

from django.shortcuts import render
from django.http import HttpResponseForbidden
from .models import User, Meeting

from django.shortcuts import render
from django.http import HttpResponseForbidden
from .models import User, Meeting

def user_list(request, list_type):
    if request.user.user_type == 'student':
        return HttpResponseForbidden("You do not have permission to access this page.")
    
    if list_type == 'students':
        if request.user.user_type == 'Tutor':
            meetings = Meeting.objects.filter(tutor=request.user)
            students = meetings.values_list('student', flat=True)
            users = User.objects.filter(id__in=students).order_by('username')
            title = "Your Students"
        else:
            users = User.objects.filter(user_type='student').order_by('username')
            title = "Student List"
            
        # Fetch current tutors for each student
        for user in users:
            user.current_tutors = Meeting.objects.filter(student=user, status='scheduled').values_list('tutor__username', flat=True)
    
    elif list_type == 'tutors':
        if request.user.user_type == 'Admin':
            users = User.objects.filter(user_type='Tutor').order_by('username')
            title = "Tutor List"
        else:
            users = []
            title = "Access Denied"
    
    else:
        users = []
        title = "Invalid List Type"

    return render(request, 'partials/lists.html', {
        'users': users,
        'title': title
    })



class TutorView(LoginRequiredMixin, View):
    
    template_name = 'tutor/dashboard_tutor.html'

    def get(self, request):
        current_user = request.user
        # Get tutor group and all users in it
        tutor_group = Group.objects.get(name='Tutor')
        tutors = tutor_group.user_set.all()
        
        context = {
            'user': current_user,
            'tutors': tutors,
            'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        }
        return render(request, self.template_name, context)
