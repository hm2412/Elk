
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from tutorials.models import TutorProfile, TutorAvailability, Meeting


# Dashboard views
from django.http import JsonResponse

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