from django.apps import AppConfig

class PreventiveConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'preventive'
    
    def ready(self):
        import preventive.signals