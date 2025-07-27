from django import forms
from .models import DashboardPreference

class DashboardPreferenceForm(forms.ModelForm):
    class Meta:
        model = DashboardPreference
        fields = ['layout_config', 'theme']
        widgets = {
            'layout_config': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation supplémentaire si nécessaire