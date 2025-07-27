from django.urls import path
from . import views

app_name = 'dashboard_app'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('save-preferences/', views.save_preferences, name='save_preferences'),
    path('notifications/read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
]