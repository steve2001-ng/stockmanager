from django import forms
from .models import ElectricityConsumption
from django.forms.widgets import DateInput

class ElectricityConsumptionForm(forms.ModelForm):
    class Meta:
        model = ElectricityConsumption
        fields = [ 'mois', 'montant']
        widgets = {
            'mois': forms.DateInput(attrs={'type': 'month'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mois'].input_formats = ['%Y-%m']
