from django import template
from datetime import date, timedelta

register = template.Library()

@register.filter
def is_due_soon(value):
    """Vérifie si une date est dans les 3 jours"""
    return value <= date.today() + timedelta(days=3)

@register.filter
def task_color(task_type):
    """Retourne une couleur Bootstrap en fonction du type de tâche"""
    colors = {
        'cleaning': 'info',
        'inspection': 'warning',
        'part_replacement': 'danger',
        'calibration': 'success'
    }
    return colors.get(task_type, 'secondary')