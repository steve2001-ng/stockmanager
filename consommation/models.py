from django.db import models
from entrepots.models import SiteEntrepot

class ElectricityConsumption(models.Model):
    site = models.ForeignKey(SiteEntrepot, on_delete=models.CASCADE, related_name='consommations')
    mois = models.DateField(verbose_name="Mois concerné")  # utiliser le 1er du mois
    montant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant de la facture (FCFA)")

    class Meta:
        unique_together = ['site', 'mois']
        ordering = ['-mois']

    def __str__(self):
        return f"{self.site.designation} - {self.mois.strftime('%B %Y')} : {self.montant} FCFA"
