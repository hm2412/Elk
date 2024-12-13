from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from tutorials.models import TutorProfile, TutorAvailability
from tutorials.forms import TutorAvailabilityForm, TutorHourlyRateForm, TutorSubjectsForm

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