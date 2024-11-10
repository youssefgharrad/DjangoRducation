from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('logout', views.log_out, name='log_out'),
    path('forgot-password', views.forgot_password, name='forgot_password'),
    path(
        "update-password/<str:token>/<str:uid>/",
        views.update_password,
        name="update_password",
    ),
    path('profile', views.profile, name='profile'),
    path('update_profile', views.update_profile, name='update_profile'),





]
