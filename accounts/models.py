# models.py dans le dossier accounts
from django.contrib.auth.models import AbstractUser
from django.db import models
class CustomUser(AbstractUser):
    ROLES = [
        ('Etudiant', 'Étudiant'),
        ('Enseignant', 'Enseignant'),
    ]
    EXPERIENCES = [
        ('Débutant', 'Débutant'),
        ('Intermédiaire', 'Intermédiaire'),
        ('Avancé', 'Avancé'),
    ]
    SPECIALITES = [
        ('Développement Web', 'Développement Web'),
        ('Développement Mobile', 'Développement Mobile'),
        ('Développement Logiciel', 'Développement Logiciel'),
        ('Développement Jeux Vidéo', 'Développement Jeux Vidéo'),
        ('Développement Réseau', 'Développement Réseau'),
        ('Développement Système', 'Développement Système'),
        ('Développement Embarqué', 'Développement Embarqué'),
        ('Développement IA', 'Développement IA'),
        ('Développement IoT', 'Développement IoT'),
        ('Développement Cloud', 'Développement Cloud'),
        ('Développement Big Data', 'Développement Big Data'),
        ('Développement Blockchain', 'Développement Blockchain'),
        ('Développement Sécurité', 'Développement Sécurité'),
        ('Développement DevOps', 'Développement DevOps'),
        ('Développement Autre', 'Développement Autre'),
    ]

    role = models.CharField(max_length=50, choices=ROLES, default='Etudiant')
    experience = models.CharField(max_length=50, choices=EXPERIENCES, default='Débutant')
    diplomes = models.CharField(max_length=255, blank=True, null=True)
    specialite = models.CharField(max_length=100, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.username

class UserLoginAttempt(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    successful = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.timestamp} - {self.ip_address} - {self.successful}"

class UserAlert(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.created_at} - {self.is_read}"

