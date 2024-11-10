from django.db import models
from gestionCours.models import Course

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    total_questions = models.IntegerField(default=0)
    passing_score = models.DecimalField(max_digits=5, decimal_places=2, default=50.00)
    created_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.TextField()
    points = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    created_at = models.DateTimeField(auto_now_add=True)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
