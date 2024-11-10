from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import codecs
from .models import CustomUser
from django.db import IntegrityError
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import UserLoginAttempt
from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import reverse




def signup(request):
    error = False
    message = ""
    if request.method == "POST":
        name = request.POST.get('name', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        repassword = request.POST.get('repassword', None)
        role = request.POST.get('role', None)
        diplomes = request.POST.get('diplomes', None)


        if not error and password != repassword:
            error = True
            message = "Les deux mots de passe ne correspondent pas!"

        user = CustomUser.objects.filter(Q(email=email)).first()
        if user:
            error = True
            message = f"Un utilisateur avec l'email {email} existe déjà!"

        if not error:
            user = CustomUser(
                username=name,
                email=email,
                role=role,
                diplomes=diplomes



            )
            user.set_password(password)
            user.save()
            return redirect('signin')

    context = {
        'error': error,
        'message': message
    }
    return render(request, 'accounts/signup.html', context)

def signin(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = CustomUser.objects.filter(email=email).first()

        if user:
            auth_user = authenticate(username=user.username, password=password)
            if auth_user:
                UserLoginAttempt.objects.create(user=user, ip_address=request.META['REMOTE_ADDR'], successful=True)
                login(request, auth_user)
                return redirect('dashboard')
            else:
                UserLoginAttempt.objects.create(user=user, ip_address=request.META['REMOTE_ADDR'], successful=False)
                messages.error(request, "Mot de passe incorrect. Veuillez réessayer.")

                failed_attempts = UserLoginAttempt.objects.filter(user=user, successful=False).count()
                if failed_attempts >= 3:
                    print("Anomaly detected, calling notify_user")
                    notify_user(user.email)
                    messages.error(request, "Trop de tentatives de connexion infructueuses. Veuillez réessayer plus tard.")

        else:
            messages.error(request, f"Aucun utilisateur trouvé avec l'email {email}.")

    return render(request, 'accounts/login.html')

def notify_user(email):
    subject = 'Alerte de sécurité : Anomalie de connexion détectée'
    message = 'Nous avons détecté une activité suspecte sur votre compte. Veuillez vérifier votre compte.'
    from_email = settings.DEFAULT_FROM_EMAIL
    email_message = EmailMessage(subject, message, from_email, [email])
    try:
        email_message.send()
        print(f"E-mail envoyé avec succès à {email}")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail : {e}")

def check_anomalies(user):
    time_threshold = timezone.now() - timedelta(hours=1)
    suspicious_logins = UserLoginAttempt.objects.filter(user=user, successful=False, timestamp__gte=time_threshold).annotate(
        attempt_count=Count('id')
    ).filter(attempt_count__gt=2)

    for attempt in suspicious_logins:
        print(f"Anomalie détectée pour l'utilisateur {attempt.user.email}, envoi d'un email...")
        notify_user(attempt.user.email)

@login_required(login_url='signin')
def dashboard(request):
    return render(request, 'home/dashboard.html', {})

def log_out(request):
    logout(request)
    return redirect('signin')

def forgot_password(request):
    error = False
    success = False
    message = ""
    if request.method == 'POST':
        email = request.POST.get('email')
        user = CustomUser.objects.filter(email=email).first()
        if user:
            print("send eemail")
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            current_site = request.META["HTTP_HOST"]
            context = {"token": token, "uid": uid, "domaine": f"http://{current_site}"}

            html_text = render_to_string("accounts/email.html", context)
            msg = EmailMessage(
                "Modification de mot de pass!",
                html_text,
                "chouaibmoumni1212@gmail.com",
                [user.email],
            )
            msg.content_subtype = 'html'
            msg.send()
            message = "processing forgot password"
            success = True
        else:
            print("user does not exist")
            error = True
            message = "user does not exist"

    context = {
        'success': success,
        'error':error,
        'message':message
    }
    return render(request, "accounts/forgot_password.html", context)

def update_password(request, token, uid):
    try:
        user_id = urlsafe_base64_decode(uid)
        decode_uid = codecs.decode(user_id, "utf-8")
        user = CustomUser.objects.get(id=decode_uid)
    except:
        return HttpResponseForbidden(
            "Vous n'aviez pas la permission de modifier ce mot de pass. Utilisateur introuvable"
        )

    check_token = default_token_generator.check_token(user, token)
    if not check_token:
        return HttpResponseForbidden(
            "Vous n'aviez pas la permission de modifier ce mot de pass. Votre Token est invalid ou a espiré"
        )

    error = False
    success = False
    message = ""
    if request.method == "POST":
        password = request.POST.get("password")
        repassword = request.POST.get("repassword")
        print(password, repassword)
        if repassword == password:
            try:
                validate_password(password, user)
                user.set_password(password)
                user.save()

                success = True
                message = "votre mot de pass a été modifié avec succès!"
                return redirect('signin')
            except ValidationError as e:
                error = True
                message = str(e)
        else:
            error = True
            message = "Les deux mot de pass ne correspondent pas"

    context = {"error": error, "success": success, "message": message}

    return render(request, "accounts/update_password.html", context)

@login_required(login_url='signin')
def profile(request):
    user = request.user
    error = False
    message = ""

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')

        try:
            validate_email(email)
            user.email = email
        except ValidationError:
            error = True
            message = "Veuillez entrer un email valide."

        if not error:
            user.username = name
            user.save()
            messages.success(request, "Votre profil a été mis à jour avec succès!")
            return redirect('profile')

    return render(request, 'accounts/profile.html', {'user': user, 'error': error, 'message': message})

@login_required(login_url='signin')
def update_profile(request):
    user = request.user
    error = False
    success = False
    message = ""

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        about = request.POST.get('about')
        diplomes = request.POST.get('diplomes')
        experience = request.POST.get('experience')
        specialite = request.POST.get('specialite')
        avatar = request.FILES.get('avatar', None)

        if not name:
            error = True
            message = "Le nom ne peut pas être vide."

        try:
            validate_email(email)
        except ValidationError:
            error = True
            message = "Veuillez entrer un email valide."

        if not error:
            existing_user = CustomUser.objects.filter(email=email).exclude(id=user.id).first()
            if existing_user:
                error = True
                message = "Cet email est déjà utilisé par un autre utilisateur."

        if not error:
            try:
                user.username = name
                user.email = email
                user.about = about
                user.diplomes = diplomes
                user.experience = experience
                user.specialite = specialite

                if avatar:
                    user.avatar = avatar

                user.save()
                success = True
                message = "Votre profil a été mis à jour avec succès."

            except IntegrityError:
                error = True
                message = "Une erreur est survenue lors de la mise à jour de votre profil."

    context = {
        'user': user,
        'error': error,
        'success': success,
        'message': message
    }
    return render(request, 'accounts/profile.html', context)
