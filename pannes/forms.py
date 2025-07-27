from django import forms
from .models import Panne
from equipments.models import Equipment, SousEnsemble
from django.utils import timezone

class PanneForm(forms.ModelForm):
    class Meta:
        model = Panne
        fields = '__all__'
        widgets = {
            'date_heure_panne': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipement'].queryset = Equipment.objects.all().order_by('designation')  # ou 'code' selon votre besoin
        self.fields['date_heure_panne'].initial = timezone.now().strftime('%Y-%m-%dT%H:%M')

class FailureRateFilterForm(forms.Form):
    PERIOD_CHOICES = [
        ('week',  'Semaine'),
        ('month', 'Mois'),
        ('year',  'Année'),
    ]
    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        label="Période",
        initial='month',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
        