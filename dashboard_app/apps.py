from django.apps import AppConfig

class DashboardAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard_app'

    def ready(self):
        # Importez les signaux uniquement après que les apps soient chargées
        from django.conf import settings
        if not settings.configured:
            return
        try:
            import dashboard_app.signals
        except ImportError:
            pass