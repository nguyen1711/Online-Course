from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Lesson, Enrollment, Question, Choice, Submission
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    
    selected_choice_ids = []
    for key, value in request.POST.items():
        if key.startswith('choice_'):
            selected_choice_ids.append(int(value))
            
    for choice_id in selected_choice_ids:
        choice = Choice.objects.get(id=choice_id)
        submission.choices.add(choice)
        
    submission.save()
    return HttpResponseRedirect(reverse('onlinecourse:show_exam_result', args=(course.id, submission.id)))

def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    total_score = 0
    questions = course.question_set.all()
    selected_choice_ids = [c.id for c in submission.choices.all()]
    
    for question in questions:
        if question.is_get_score(selected_choice_ids):
            total_score += question.grade
            
    context = {
        'course': course,
        'selected_ids': selected_choice_ids,
        'grade': total_score,
        'submission': submission
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
