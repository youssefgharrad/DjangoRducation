from django.urls import path
from . import views

urlpatterns = [
    path('course/', views.courses_list, name='courses_list'),
    path('courses-add', views.add_course, name='courses_add'),
    path('courses/<int:course_id>/update/', views.update_course, name='courses_update'),
    path('courses/<int:course_id>/delete/', views.delete_course, name='courses_delete'),
    path('course/<int:course_id>', views.courses_selectionner, name='courses_selectionner'),
    path('course/<int:course_id>/chapitre/add/', views.add_chapitre, name='add_chapitre'),
    path('course/chapitre/view_chapitre/', views.toggle_view_chapitre, name='toggle_view_chapitre'),
    path('summarize_pdf/<int:chapter_id>/', views.summarize_pdf, name='summarize_pdf'),
    path('chapitres/<int:chapter_id>/delete/', views.delete_chapitre, name='chapitres_delete'),

    path('cours/<int:course_id>/participer/', views.participer_cours, name='participer_cours'),
    path('cours-participer', views.mes_cours_participes, name='mes_cours_participes'),
    path('courses-recommend', views.recommend_courses, name='courses'),

    
]
