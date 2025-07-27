# dashboard_app/middleware.py
from django.conf import settings
from .models import DashboardPreference

class EnsurePreferencesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            DashboardPreference.objects.get_or_create(user=request.user)
        return self.get_response(request)