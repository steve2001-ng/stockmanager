from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import DashboardPreference, UserNotification
from .forms import DashboardPreferenceForm
from django.http import JsonResponse
from pannes.services import get_pannes_stats
from stockapp.utils import get_nombre_alertes
from preventive.models import get_due_preventive_tasks, PreventiveTask
from datetime import date
from django.utils.timezone import now
from consommation.models import ElectricityConsumption
from django.db.models import Max
from messagerie.models import Message

@login_required
def dashboard(request):
    # Statistiques pannes et alertes
    pannes_stats = get_pannes_stats()
    nb_alertes = get_nombre_alertes()

    # Préférences et notifications
    preferences, _ = DashboardPreference.objects.get_or_create(user=request.user)
    notifications = UserNotification.objects.filter(user=request.user, is_read=False)[:5]

    # Marquer les tâches préventives manquées
    today = now().date()
    PreventiveTask.objects.filter(status='pending', next_due__lt=today).update(status='missed')

    # Tâches préventives dues
    due_tasks = get_due_preventive_tasks()
    due_tasks_count = due_tasks.count()

    # Statistiques des tâches
    total_tasks = PreventiveTask.objects.count()
    completed = PreventiveTask.objects.filter(status='completed').count()
    missed = PreventiveTask.objects.filter(status='missed').count()
    upcoming = PreventiveTask.objects.filter(status='pending', next_due__gte=today).count()
    if total_tasks > 0:
        completion_rate = round((completed / total_tasks) * 100, 1)
        missed_rate = round((missed / total_tasks) * 100, 1)
    else:
        completion_rate = missed_rate = 0

    # Montant maximal de facture électrique (toutes consommations)
    max_montant = ElectricityConsumption.objects.aggregate(
        max_montant=Max('montant')
    )['max_montant'] or 0

    # Compter les messages que l'utilisateur n'a pas lus
    unread_messages_count = Message.objects.exclude(read_by=request.user).count()

    context = {
        'preferences': preferences,
        'notifications': notifications,
        'active_page': 'dashboard',
        'total_pannes': pannes_stats['total'],
        'nb_alertes': nb_alertes,
        'due_tasks': due_tasks,
        'due_tasks_count': due_tasks_count,
        'completion_rate': completion_rate,
        'missed_tasks': missed,
        'missed_rate': missed_rate,
        'upcoming_tasks': upcoming,
        'max_montant': max_montant,
        'unread_messages_count': unread_messages_count,
    }
    return render(request, 'dashboard_app/dashboard.html', context)

@login_required
def save_preferences(request):
    if request.method == 'POST':
        form = DashboardPreferenceForm(request.POST, instance=request.user.dashboardpreference)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def mark_notification_read(request, pk):
    try:
        notification = UserNotification.objects.get(pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except UserNotification.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)
