# gestionQuiz/urls.py

from django.urls import path
from .views import create_quiz, quiz_list, update_quiz, delete_quiz , quiz_detail , edit_quiz , generate_and_take_quiz

urlpatterns = [
    path('', quiz_list, name='quiz_list'),
    path('create/', create_quiz, name='create_quiz'),
    path('update/<int:pk>/', update_quiz, name='update_quiz'),
    path('delete/<int:pk>/', delete_quiz, name='delete_quiz'),
    path('quizzes/<int:quiz_id>/', quiz_detail, name='quiz_detail'),
    path('quizzes/<int:pk>/edit/', edit_quiz, name='edit_quiz'),
    path('generate_quiz/<int:course_id>/', generate_and_take_quiz, name='generate_quiz'),

]
