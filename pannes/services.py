# pannes/services.py
from django.db.models import Count
from .models import Panne
from django.utils import timezone


def get_pannes_stats():
    return {
        'total': Panne.objects.count(),
        'today': Panne.objects.filter(date_heure_panne__date=timezone.now().date()).count(),
        'week': Panne.objects.filter(date_heure_panne__week=timezone.now().isocalendar()[1]).count(),
        'month': Panne.objects.filter(date_heure_panne__month=timezone.now().month).count()
    }