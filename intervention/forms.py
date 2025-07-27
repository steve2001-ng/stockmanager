from django import forms
from .models import DemandeIntervention, OrdreTravail, RapportIntervention
from pannes.models import Panne
from equipments.models import Equipment, SousEnsemble

class DemandeInterventionForm(forms.ModelForm):
    panne = forms.ModelChoiceField(
        queryset=Panne.objects.filter(resolue=False),
        label="Panne associée",
        required=True
    )
    
    class Meta:
        model = DemandeIntervention
        fields = ['panne', 'equipement', 'urgence', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipement'].disabled = True
        
        if 'panne' in self.data:
            try:
                panne_id = int(self.data.get('panne'))
                panne = Panne.objects.get(id=panne_id)
                self.fields['equipement'].initial = panne.equipement
            except (ValueError, Panne.DoesNotExist):
                pass
        elif self.instance.pk:
            self.fields['equipement'].initial = self.instance.panne.equipement

class OrdreTravailForm(forms.ModelForm):
    sous_ensemble = forms.ModelChoiceField(
        queryset=SousEnsemble.objects.all(),
        required=False,
        label="Sous-ensemble concerné"
    )
    
    class Meta:
        model = OrdreTravail
        fields = ['demande', 'equipement', 'sous_ensemble', 'date_planifiee', 'equipe', 'description', 'statut']
        widgets = {
            'date_planifiee': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super().__init__(*args, **kwargs)
        # Si on est en modification (instance.pk existe), on verrouille l’équipement
        if self.instance and self.instance.pk:
            # On ne veut pas permettre de changer l’équipement sur un ordre existant
            # On affiche l’équipement en champ masqué (et on conserve sa valeur)
            self.fields['equipement'].widget = forms.HiddenInput()
            self.fields['equipement'].disabled = True

        # Sinon (création), on propose tous les équipements disponibles
        else:
            self.fields['equipement'].queryset = Equipment.objects.all()

class RapportInterventionForm(forms.ModelForm):
    class Meta:
        model = RapportIntervention
        fields = ['ordre', 'description', 'actions', 'pieces_utilisees', 'temps_passe', 'statut']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'actions': forms.Textarea(attrs={'rows': 4}),
            'pieces_utilisees': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Par défaut, on propose tous les ordres dont le statut est "En cours"
        self.fields['ordre'].queryset = OrdreTravail.objects.all()