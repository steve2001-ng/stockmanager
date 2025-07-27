from django import forms
from .models import Equipment, SousEnsemble

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = '__all__'
        widgets = {
            'family': forms.Select(attrs={'class': 'form-control'}),
            'sub_family': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'site': forms.Select(attrs={'class': 'form-control'}),
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'group_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'power_per_group': forms.NumberInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'temperature_setpoint': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'commissioning_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'documentation': forms.FileInput(attrs={'class': 'form-control'}),
        }

class SousEnsembleForm(forms.ModelForm):
    class Meta:
        model = SousEnsemble
        fields = ['type', 'code', 'designation', 'parent', 'caracteristiques', 'image']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'caracteristiques': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Ex : puissance = 10kW, fluide = R404A'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        equipement = kwargs.pop('equipement', None)
        super().__init__(*args, **kwargs)

        if equipement:
            self.fields['parent'].queryset = SousEnsemble.objects.filter(equipement=equipement)

        ''' # Si le champ contient du JSON brut, on essaie de le formater joliment
        if self.instance and self.instance.caracteristiques:
            try:
                import json
                data = json.loads(self.instance.caracteristiques)
                pretty_text = '\n'.join(f"{k} = {v}" for k, v in data.items())
                self.initial['caracteristiques'] = pretty_text
            except Exception:
                pass  # ce n’est pas du JSON, donc on garde tel quel'''
