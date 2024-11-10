from django.urls import path
from . import views


urlpatterns = [
    path("my-todos/", views.todo_list, name="user_todo_list"),
    path("create/", views.create_task, name="create_task"),  # Vue de création de tâche
    path(
        "update/<int:pk>/", views.update_task, name="update_task"
    ),  # Route pour mettre à jour une tâche
    path('todo/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('todo/<int:task_id>/complete/', views.complete_task, name='complete_task'),  # Nouvelle URL
    path('todo/downloadtask', views.download_tasks_pdf, name='download_tasks_pdf'),  # Nouvelle URL
    path('todo/organized', views.user_todo_list, name='Organized_tache'),  # Nouvelle URL


]
