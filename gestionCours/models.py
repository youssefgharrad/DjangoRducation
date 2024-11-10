from django.db import models
from django.conf import settings

class Course(models.Model):
    TITLE_CHOICES = [
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

    title = models.CharField(max_length=255)
    description = models.TextField()
    specialites = models.CharField(max_length=100, choices=TITLE_CHOICES)
    niveau = models.CharField(max_length=50, choices=[('Débutant', 'Débutant'), ('Intermédiaire', 'Intermédiaire'), ('Avancé', 'Avancé')], default='Débutant')
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='courses/images/', blank=True, null=True)
    pdf = models.FileField(upload_to='courses/pdfs/', blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enseignant_courses')

    def __str__(self):
        return self.title


class Chapitre(models.Model):

    CATEGORIE_CHOICES = [
        ('Introduction', 'Introduction'),
        ('Les Bases', 'Les Bases'),
        ('Sujets Avancés', 'Sujets Avancés'),
        ('Études de Cas', 'Études de Cas'),
        ('Théorie', 'Théorie'),
        ('Applications Pratiques', 'Applications Pratiques'),
        ('Exercises', 'Exercices'),
        ('Résumé', 'Résumé'),
        ('Révision', 'Révision'),
        ('Travail de Projet', 'Travail de Projet'),
        ('Matériel Supplémentaire', 'Matériel Supplémentaire'),
        ('Exemples Concrets', 'Exemples Concrets'),
        ('Questions Fréquemment Posées (FAQ)', 'Questions Fréquemment Posées (FAQ)'),
        ('Meilleures Pratiques', 'Meilleures Pratiques'),
        ('Références', 'Références'),
        ('Ressources Complémentaires', 'Ressources Complémentaires'),
        ('Devoirs', 'Devoirs'),
        ('Laboratoires et Expériences', 'Laboratoires et Expériences'),
        ('Outils et Techniques', 'Outils et Techniques'),
        ('Conclusion', 'Conclusion'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    categorie = models.CharField(max_length=100, choices=CATEGORIE_CHOICES, blank=True, null=True)
    document = models.FileField(upload_to='chapitre/documents/', blank=True, null=True)
    viewChapitre = models.BooleanField(default=False)
    cours = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapitres')

    def __str__(self):
        return f"{self.title} - {self.cours.title}"


class Summarize(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    cours = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='summaries')
    categorie = models.CharField(max_length=100, blank=True, null=True)
    pdf = models.FileField(upload_to='sumarized/pdfs/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.cours.title}"


class CoursParticiperParUser(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='participations')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_participations')
    date_participation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User: {self.user.username}, Course: {self.course.title}, Date: {self.date_participation}"
