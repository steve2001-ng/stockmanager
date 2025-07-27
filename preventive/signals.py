from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PreventiveTask
from django.utils import timezone
from datetime import timedelta

@receiver(post_save, sender=PreventiveTask)
def update_next_due_date(sender, instance, created, **kwargs):
    if instance.is_completed and instance.frequency_days:
        instance.last_performed = timezone.now().date()
        instance.next_due = instance.last_performed + timedelta(days=instance.frequency_days)
        instance.is_completed = False
        instance.save()