from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class DashboardPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboard_preferences'
    )
    layout_config = models.JSONField(default=dict)
    theme = models.CharField(max_length=20, default='light')

    def __str__(self):
        return f"Préférences de {self.user.username}"

class UserNotification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification pour {self.user.username}"

# Signal pour créer des préférences par défaut
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_preferences(sender, instance, created, **kwargs):
    if created:
        DashboardPreference.objects.create(user=instance)