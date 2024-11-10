from django.urls import path
from . import views

urlpatterns = [
    path('translate/', views.gradio_view, name='gradio_view'),
    path('translatorhistory/', views.translator_history, name='translator_history'),
    path('translations/<int:translation_id>/', views.delete_translation, name='delete_translation'),


]
