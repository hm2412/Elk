
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from tutorials.models import Lesson
from tutorials.forms import LessonRequestForm, ReviewForm
from tutorials.helpers import user_role_required

@login_required
@user_role_required(['Student', 'Admin'])
def create_lesson_request(request):
    """Allow students and admins to create lesson requests"""
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
@user_role_required(['Student', 'Admin'])
def view_lesson_request(request):
    """Allow students and admins to view lesson requests"""
    # Remove the student-only check since we use the decorator
    lesson = Lesson.objects.filter(student=request.user).first()
    
    lesson_requests = Lesson.objects.filter(student=request.user).order_by('id')
    paginator = Paginator(lesson_requests, 10)  # 10 per page 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'view_lesson_request.html', {
        'lesson': lesson,
        'lesson_requests': page_obj
    })

@login_required
def submit_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.student = request.user  # Ensure the logged-in user is assigned
            review.save()

            messages.success(request, 'Thank you for your feedback!')

            return redirect('submit_review')  # Redirect to the same page to show the message
    else:
        form = ReviewForm()

    return render(request, 'review.html', {
        'review': form, 
        'is_review_page': True  # This will ensure 'review.css' is loaded
    })
