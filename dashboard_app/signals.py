from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import DashboardPreference

User = get_user_model()

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_preferences(sender, instance, created, **kwargs):
    """Crée des préférences par défaut pour tout nouvel utilisateur"""
    if created:
        DashboardPreference.objects.get_or_create(user=instance)