from django.db import models
from django.utils import timezone
from datetime import date
from equipments.models import Equipment  # Supposant que c'est votre modèle existant

class TemperatureReading(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='temperature_readings')
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    reading_date = models.DateField(default=timezone.now)
    reading_time = models.TimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    recorded_by = models.CharField(max_length=100)

    class Meta:
        ordering = ['-reading_date', '-reading_time']
        verbose_name = "Relevé de température"
        
    def __str__(self):
        return f"{self.equipment.name} - {self.temperature}°C - {self.reading_date}"


class PreventiveTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Effectuée'),
        ('postponed', 'Reportée'),
        ('incomplete', 'Inachevée'),
        ('missed', 'Manquée'),
    ]
    TASK_TYPES = [
        ('cleaning', 'Nettoyage'),
        ('inspection', 'Inspection'),
        ('part_replacement', 'Remplacement de pièce'),
        ('calibration', 'Étalonnage'),
    ]

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    description = models.TextField()
    frequency_days = models.PositiveIntegerField(default=30)  # ➕ Fréquence en jours
    last_performed = models.DateField(null=True, blank=True)  # ➕ Date de dernière réalisation
    next_due = models.DateField()
    duration_hours = models.DecimalField(max_digits=4, decimal_places=1)
    assigned_to = models.CharField(max_length=100)
    is_completed = models.BooleanField(default=False)
    color_code = models.CharField(max_length=7, default='#6c757d')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    postponed_to = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        color_map = {
            'cleaning': '#0dcaf0',
            'inspection': '#ffc107',
            'part_replacement': '#dc3545',
            'calibration': '#20c997',
        }
        self.color_code = color_map.get(self.task_type, '#6c757d')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_task_type_display()} - {self.equipment.designation}"
    
    def is_overdue(self):
        return self.status == 'pending' and self.next_due < timezone.now().date()

    def get_status_badge(self):
        badge_classes = {
            'pending': 'badge bg-warning text-dark',
            'completed': 'badge bg-success',
            'postponed': 'badge bg-info text-dark',
            'incomplete': 'badge bg-secondary',
            'missed': 'badge bg-danger',
        }
        return f'<span class="{badge_classes.get(self.status, "badge bg-light")}">{self.get_status_display()}</span>'

def get_due_preventive_tasks():
    return PreventiveTask.objects.filter(is_completed=False, next_due__lte=date.today())