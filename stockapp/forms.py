from django import forms
from .models import Produit, Commande
from .models import MouvementStock

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['code', 'famille', 'designation', 'fournisseur', 
                 'caracteristiques', 'quantite', 'stock_alerte', 'image']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'caracteristiques': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Décrivez les caractéristiques techniques...'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            }),
        }
        labels = {
            'caracterisqtiques': 'Caractéristiques techniques',
            'quantite': 'Qté en stock'
        }

class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['designation', 'caracteristiques', 'quantite', 'objet', 'initie_par']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'caracteristiques': forms.Textarea(attrs={'rows': 3}),
        }


class MouvementStockForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = ['produit', 'type', 'quantite', 'motif']
        widgets = {
            'motif': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            
        }
