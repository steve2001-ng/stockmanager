from django import forms
from django.utils import timezone
from .models import TemperatureReading, PreventiveTask
from equipments.models import Equipment

class TemperatureReadingForm(forms.ModelForm):
    equipment = forms.ModelChoiceField(
        queryset=Equipment.objects.all().order_by('designation'),
        label="Équipement",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required'
        })
    )
    class Meta:
        model = TemperatureReading
        fields = ['equipment', 'temperature', 'reading_date', 'reading_time', 'notes', 'recorded_by']
        widgets = {
            'reading_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'jj/mm/aaaa'
            }),
            'reading_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'value': '09:30'
            }),
            'temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes supplémentaires...'
            }),
            'recorded_by': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'Utilisateur'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['reading_date'].initial = timezone.now().date()
        self.fields['reading_time'].initial = timezone.now().time().strftime('%H:%M')
        self.fields['recorded_by'].initial = 'Utilisateur'  # À remplacer par l'utilisateur connecté
        # Debug: Vérifiez le queryset dans la console
        print("Nombre d'équipements trouvés:", Equipment.objects.count())
        print("Premier équipement:", Equipment.objects.first())
        
        self.fields['equipment'].queryset = Equipment.objects.all().order_by('designation')
       
    def clean(self):
        cleaned_data = super().clean()
        print("Données validées:", cleaned_data)  # Debug
        return cleaned_data
    
class PreventiveTaskForm(forms.ModelForm):
    class Meta:
        model = PreventiveTask
        fields = [
            'equipment', 'task_type', 'description',
            'frequency_days', 'last_performed',
            'next_due', 'duration_hours', 'assigned_to', 'status', 'postponed_to',
        ]
        widgets = {
            'equipment': forms.Select(attrs={'class': 'form-select'}),
            'task_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'frequency_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'last_performed': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'next_due': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'assigned_to': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'postponed_to': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipment'].queryset = Equipment.objects.all().order_by('designation')

    def clean(self):
        cleaned_data = super().clean()
        print("Données validées:", cleaned_data)
        return cleaned_data
