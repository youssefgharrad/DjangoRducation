# gestionQuiz/views.py
import json
import re

from async_timeout import Timeout
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from google.generativeai import GenerativeModel
from requests import RequestException

import settings

from gestionCours.models import Course
from .models import Quiz
from .forms import QuizForm, QuestionForm, ChoiceForm
import requests
import os
import google.generativeai as genai
from django.http import HttpResponse
from django.shortcuts import render
from google.generativeai.types import GenerationConfig
genai.configure(api_key=settings.GEMINI_API_KEY)  # Set your API key in environment variables

def create_quiz(request):
    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        total_questions = int(request.POST.get('total_questions', 0))

        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            all_valid = True  # Track overall form validity
            question_instances = []  # Store valid questions to save later
            choice_instances = []  # Store valid choices to save later

            # Process each question and its choices
            for i in range(total_questions):
                # Collect data for each question
                question_data = {
                    'question_text': request.POST.get(f'question_{i}-question_text'),
                    'question_type': request.POST.get(f'question_{i}-question_type'),
                    'points': request.POST.get(f'question_{i}-points', 1),
                }
                question_form = QuestionForm(question_data)

                if question_form.is_valid():
                    question = question_form.save(commit=False)
                    question.quiz = quiz
                    question_instances.append(question)
                else:
                    all_valid = False  # Mark as invalid if any question form fails
                    continue  # Skip processing choices if question is invalid

                # Process choices only if the question is valid
                choice_count = len([key for key in request.POST if key.startswith(f'choice_{i}_')])
                for j in range(1, choice_count + 1):
                    choice_data = {
                        'choice_text': request.POST.get(f'choice_{i}_{j}-choice_text'),
                        'is_correct': request.POST.get(f'correct_choice_{i}') == f'choice_{i}_{j}'
                    }
                    choice_form = ChoiceForm(choice_data)

                    if choice_form.is_valid():
                        choice = choice_form.save(commit=False)
                        choice.question = question  # Link choice to question
                        choice_instances.append(choice)
                    else:
                        all_valid = False  # Mark as invalid if any choice form fails

            # Save quiz, questions, and choices only if all forms are valid
            if all_valid:
                quiz.save()
                for question in question_instances:
                    question.save()
                for choice in choice_instances:
                    choice.save()
                return redirect('quiz_list')
            else:
                print("One or more forms were invalid.")
        else:
            print("Quiz form was invalid.")

    else:
        quiz_form = QuizForm()
        question_forms = [QuestionForm(prefix=f'question_{i}') for i in range(5)]
        choice_forms_list = [[ChoiceForm(prefix=f'choice_{i}_{j}') for j in range(1, 6)] for i in range(5)]

    return render(request, 'gestionQuiz/quiz_form.html', {
        'quiz_form': quiz_form,
    })





# List Quizzes
def quiz_list(request):
    quizzes = Quiz.objects.all()
    return render(request, 'gestionQuiz/quiz_list.html', {'quizzes': quizzes})

# Update a Quiz
def update_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            return redirect('quiz_list')  # Redirect to the list of quizzes after updating
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'gestionQuiz/quiz_form.html', {'form': form})

# Delete a Quiz
def delete_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.method == 'POST':
        quiz.delete()
        return redirect('quiz_list')  # Redirect to the list of quizzes after deleting
    return render(request, 'gestionQuiz/quiz_confirm_delete.html', {'quiz': quiz})

from django.shortcuts import render, get_object_or_404
from .models import Quiz

def quiz_detail(request, quiz_id):
    # Retrieve the quiz along with related questions and choices
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    questions = quiz.questions.prefetch_related('choices')

    return render(request, 'gestionQuiz/quiz_detail.html', {
        'quiz': quiz,
        'questions': questions
    })


# views.py
from django.shortcuts import get_object_or_404, redirect, render
from .forms import QuizForm, QuestionForm, ChoiceForm
from .models import Quiz, Question, Choice
from django.forms import inlineformset_factory


def edit_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)

    # Create form instances for the Quiz, Question, and Choices.
    if request.method == 'POST':
        quiz_form = QuizForm(request.POST, instance=quiz)
        QuestionFormSet = inlineformset_factory(Quiz, Question, form=QuestionForm, extra=1)
        question_formset = QuestionFormSet(request.POST, instance=quiz)

        if quiz_form.is_valid() and question_formset.is_valid():
            quiz_form.save()
            question_formset.save()
            return redirect('quiz_detail', quiz.id)
    else:
        quiz_form = QuizForm(instance=quiz)
        QuestionFormSet = inlineformset_factory(Quiz, Question, form=QuestionForm, extra=1)
        question_formset = QuestionFormSet(instance=quiz)

    return render(request, 'gestionQuiz/edit_quiz.html', {
        'quiz_form': quiz_form,
        'question_formset': question_formset,
        'quiz': quiz,
    })

import re
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import Course, Quiz, Question, Choice


import re
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import Course, Quiz, Question, Choice

def generate_and_take_quiz(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    course_name = "Java"
    num_questions = 10

    prompt = (
        f"Generate a quiz for the course '{course_name}'. The quiz should contain exactly 10 multiple-choice questions. "
        f"Each question should follow this format:\n"
        "## Question:\n<question text>\n"
        "## Type:\n<Single or Multiple Choice>\n"
        "## Points:\n<points>\n"
        "## Choices:\n"
        "a) <choice 1>\n"
        "b) <choice 2>\n"
        "c) <choice 3>\n"
        "d) <choice 4>\n"
        "## Correct Answer:\n<correct answer letter>\n\n"
        "Ensure that each question strictly follows this format and includes exactly four choices."
    )

    try:
        # Step 2: Generate quiz content
        model = GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            generation_config=GenerationConfig(
                max_output_tokens=3000,
                temperature=0.7
            )
        )
        quiz_data = response.text

        quiz = Quiz.objects.create(
            course=course,
            title=f"{course.title} Quiz",
            description="Auto-generated quiz",
            total_questions=0
        )

        question_pattern = re.compile(
            r"## Question\s*\d*:\s*(.*?)\s*## Type:\s*(Single Choice|Multiple Choice)\s*## Points:\s*(\d+)\s*## Choices:\s*((?:[abcd]\)\s*.*?)+)\s*## Correct Answer:\s*([abcd])",
            re.DOTALL
        )
        choice_pattern = re.compile(r"(a|b|c|d)\)\s*(.*?)\s*(?=(?:[abcd]\)|$))", re.DOTALL)

        total_questions = 0
        for question_match in question_pattern.finditer(quiz_data):
            total_questions += 1
            question_text = question_match.group(1).strip()
            question_type = question_match.group(2).strip()
            points = int(question_match.group(3).strip())
            choices_text = question_match.group(4).strip()
            correct_answer = question_match.group(5).strip().lower()

            question = Question.objects.create(
                quiz=quiz,
                question_text=question_text,
                points=points,
                question_type=question_type
            )

            for choice_match in choice_pattern.finditer(choices_text):
                choice_letter = choice_match.group(1).strip().lower()
                choice_text = choice_match.group(2).strip()
                is_correct = (choice_letter == correct_answer)

                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=is_correct
                )

        quiz.total_questions = total_questions
        quiz.save()

    except Exception as e:
        return render(request, 'gestionQuiz/error.html', {"message": f"An error occurred: {str(e)}"})

    # Handle form submission for scoring
    if request.method == 'POST':
        # Log entire POST request for debugging
        print("Full POST Data:", request.POST)

        # Explicitly fetch questions related to the quiz
        questions = Question.objects.filter(quiz=quiz).prefetch_related('choices')
        score = 0

        for key, value in request.POST.items():
            # Skip non-question items, like the CSRF token
            if not key.startswith("question_"):
                continue

            # Extract question ID from key
            question_id = int(key.split("_")[1])
            try:
                question = Question.objects.get(id=question_id)
            except Question.DoesNotExist:
                print(f"Question ID {question_id} not found.")
                continue

            # Fetch correct choices for this question
            correct_choices = question.choices.filter(is_correct=True)
            correct_choice_ids = set(correct_choices.values_list('id', flat=True))

            # Process user answers
            user_answers = request.POST.getlist(key)  # User answers for this question (could be multiple)
            user_answer_ids = set(map(int, user_answers))

            print(f"Question ID: {question_id}")
            print(f"User Answers: {user_answer_ids}")
            print(f"Correct Choices: {correct_choice_ids}")

            # Scoring for Single Choice
            if question.question_type == "Single Choice":
                # Single choice should have one answer
                if user_answer_ids and correct_choices.filter(id=list(user_answer_ids)[0]).exists():
                    score += question.points
                    print(f"Correct single choice for question {question_id}")

            # Scoring for Multiple Choice
            elif question.question_type == "Multiple Choice":
                # Correct answer if user selected all and only the correct options
                if user_answer_ids == correct_choice_ids:
                    score += question.points
                    print(f"Correct multiple choice for question {question_id}")

        # Calculate total points
        total_points = sum(q.points for q in questions)
        print(f"Final Score: {score}, Total Points: {total_points}")

        return JsonResponse({'score': score, 'total_points': total_points})

    # Render quiz form if GET request
    questions = Question.objects.filter(quiz=quiz).prefetch_related('choices')
    return render(request, 'gestionQuiz/take_quiz.html', {
        'quiz': quiz,
        'questions': questions
    })








