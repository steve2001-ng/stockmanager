# forms.py
from django import forms
from .models import SiteEntrepot

class SiteEntrepotForm(forms.ModelForm):
    class Meta:
        model = SiteEntrepot
        fields = '__all__'
