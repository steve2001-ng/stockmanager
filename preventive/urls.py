from django.urls import path
from .views import (TemperatureReadingListView, TemperatureReadingCreateView,
                   PreventiveTaskListView, PreventiveTaskCalendarView, TemperatureReadingListView,
    TemperatureReadingUpdateView,
    TemperatureReadingDeleteView,
    TemperatureReadingDetailView, PreventiveCalendarView, 
    PreventiveTaskCreateView, PreventiveTaskUpdateView, PreventiveTaskDeleteView)

app_name = 'preventive'

urlpatterns = [
    path('temperature/', TemperatureReadingListView.as_view(), name='temperature_readings'),
    path('temperature/new/', TemperatureReadingCreateView.as_view(), name='temperature_reading_create'),
    path('preventive/', PreventiveTaskListView.as_view(), name='preventive_tasks'),
    path('preventive/calendar/', PreventiveTaskCalendarView.as_view(), name='preventive_calendar'),
    path('temperature/reading/', PreventiveTaskListView.as_view(), name='temperature_reading_form'),
    path('temperature/', TemperatureReadingListView.as_view(), name='temperature_readings'),
    path('temperature/<int:pk>/edit/', TemperatureReadingUpdateView.as_view(), name='temperature_reading_update'),
    path('temperature/<int:pk>/delete/', TemperatureReadingDeleteView.as_view(), name='temperature_reading_delete'),
    path('temperature/<int:pk>/', TemperatureReadingDetailView.as_view(), name='temperature_reading_detail'),
    path('calendar/', PreventiveCalendarView.as_view(), name='calendar'),
    path('task/new/', PreventiveTaskCreateView.as_view(), name='task_create'),
    path('task/<int:pk>/edit/', PreventiveTaskUpdateView.as_view(), name='task_update'),
    path('task/<int:pk>/delete/', PreventiveTaskDeleteView.as_view(), name='task_delete'),
]