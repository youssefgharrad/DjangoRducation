from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include  # Assurez-vous que 'include' est importé
from django.conf.urls.static import static
from django.conf import settings


# Define a view to handle the root URL redirection
def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('accounts/dashboard')  # Redirect to a logged-in page, like the home page in gestionCours
    return redirect('/accounts/signin/')  # Redirect to login if not authenticated


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('gestionCours/', include('gestionCours.urls')),
    path('chatbot/', include('chatbot.urls')),  # This allows the chatbot to be accessed from any route
    path('todo/', include('todo.urls')),  # This allows the chatbot to be accessed from any route


    # Root URL redirects to the appropriate view based on authentication
    path('', home_redirect, name='home_redirect'),
    path('langues/', include('gestionLangue.urls')),  # Include the translate app's URLs
    path('quizzes/', include('gestionQuiz.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
