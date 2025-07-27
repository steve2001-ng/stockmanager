from django.contrib import admin
from .models import TemperatureReading, PreventiveTask
from .models import PreventiveTask



@admin.register(TemperatureReading)
class TemperatureReadingAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'temperature', 'reading_date', 'reading_time', 'recorded_by')
    list_filter = ('equipment', 'reading_date')
    search_fields = ('equipment__name', 'recorded_by')

@admin.register(PreventiveTask)
class PreventiveTaskAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'task_type', 'next_due', 'is_completed')
    list_filter = ('task_type', 'is_completed', 'equipment')
    search_fields = ('equipment__name', 'description')
    date_hierarchy = 'next_due'