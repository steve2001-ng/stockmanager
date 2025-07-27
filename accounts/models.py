from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class CustomUser(AbstractUser):
    is_administrator = models.BooleanField(
        default=False,
        verbose_name="Administrateur" )
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    
    STATUS_CHOICES = [
        ('SERVICE', 'En service'),
        ('CONGE', 'En congé'),
        ('MISSION', 'En mission'),
    ]
    @property
    def dashboard_preferences(self):
        from dashboard_app.models import DashboardPreference
        pref, created = DashboardPreference.objects.get_or_create(user=self)
        return pref
    
    # Champs supplémentaires
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Sexe")
    cni_number = models.CharField(max_length=20, verbose_name="N° court CNI")
    qualification = models.CharField(max_length=100, verbose_name="Qualification")
    city = models.CharField(max_length=100, verbose_name="Ville")
    site = models.CharField(max_length=100, verbose_name="Site")
    profile_picture = models.ImageField(upload_to='profile_pics/', verbose_name="Photo de profil")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='SERVICE', verbose_name="Statut")
    
    permissions = [
            ("access_admin_panel", "Peut accéder au panel admin"),
        ]
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

class Team(models.Model):
    """Représente une équipe de maintenance composée d’utilisateurs."""
    SPECIALTY_CHOICES = [
        ('SOU', 'Soudure'),
        ('FUI', 'Fuites'),
        ('ELE', 'Électricité'),
        ('AUT', 'Autre'),
    ]
    STATUS_CHOICES = [
        ('INTRV', 'En intervention'),
        ('BOOK', 'Réservée'),
        ('AVAIL', 'Disponible'),
    ]

    code = models.CharField(
        max_length=8,
        unique=True,
        editable=False,
        help_text="Code unique généré automatiquement"
    )
    members = models.ManyToManyField(
        CustomUser,
        related_name='teams',
        help_text="Membres de l’équipe"
    )
    specialty = models.CharField(
        max_length=3,
        choices=SPECIALTY_CHOICES,
        verbose_name="Spécialité"
    )
    status = models.CharField(
        max_length=5,
        choices=STATUS_CHOICES,
        default='AVAIL',
        verbose_name="Statut"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Génération automatique du code s’il n’existe pas encore
        if not self.code:
            # UUID court en majuscules
            self.code = uuid.uuid4().hex.upper()[:8]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_specialty_display()} ({self.code}) — {self.get_status_display()}"