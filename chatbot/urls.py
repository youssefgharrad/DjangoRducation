from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot, name='chatbot'), 
    path('historique/', views.historiquechatbot, name='historique_chatbot'),  # Catch-all for any path under 'chatbot/'
    path('delete_chats/<str:date>/', views.delete_chats_by_date, name='delete_chats_by_date'),  # New URL for deleting chats by date

]
