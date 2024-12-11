"""Forms for the tutorials app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User
from .models import Meeting

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    user_type = forms.ChoiceField(
        choices = User.USER_TYPES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
            user_type=self.cleaned_data.get('user_type'),
        )

        return user

class MeetingForm(forms.ModelForm):
    """Form to schedule meetings/tutoring sessions"""
    days = forms.ChoiceField(choices=Meeting.DAYS_CHOICES, widget=forms.Select, required=True)
    class Meta:
        model = Meeting
        fields = ['tutor', 'date', 'day', 'start_time', 'end_time', 'time_of_day', 'topic', 'status', 'notes']

from .models import Lesson 
from datetime import datetime, time
from django.core.exceptions import ValidationError

class LessonRequestForm(forms.ModelForm):
    TIME_CHOICES = [
        (datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time(), f"{hour:02d}:{minute:02d}")
        for hour in range(8, 21) 
        for minute in range(0, 60, 10)
    ]
    # Fields will now correspond to the model fields
    knowledge_area = forms.ChoiceField(choices=Lesson.KNOWLEDGE_AREAS, label="Knowledge Area")
    term = forms.ChoiceField(choices=Lesson.TERMS, label="Term")
    duration = forms.ChoiceField(choices=Lesson.DURATIONS, label=" Duration")
    start_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'type': 'time',
                'min': '08:00', 
                'max': '20:00', 
                'step': '600',  
            },
            format='%H:%M',
        ),
        label="Preferred Start Time (HH:MM)",
        input_formats=['%H:%M'], 
    )

    days = forms.MultipleChoiceField(
        choices=[
            ('mon', 'Monday'),
            ('tue', 'Tuesday'),
            ('wed', 'Wednesday'),
            ('thu', 'Thursday'),
            ('fri', 'Friday'),
            ('sat', 'Saturday'),
            ('sun', 'Sunday'),
        ],
        widget=forms.CheckboxSelectMultiple,
        label="Days (select days)",
    )
    venue_preference = forms.ChoiceField(choices=Lesson.VENUE_PREFERENCES, label="Venue Preference")

    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')

        min_time = time(8, 0)  
        max_time = time(20, 0)  
        
        if not min_time <= start_time <= max_time:
            raise ValidationError("The start time must be between 08:00 and 20:00.")

        return start_time

    class Meta:
        model = Lesson  # Connect the form to the LessonRequest model
        fields = ['knowledge_area', 'term', 'duration', 'start_time', 'days', 'venue_preference']
