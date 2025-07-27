from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from equipments.models import Equipment
from pannes.models import Panne
from django.conf import settings

STATUT_DEMANDE = (
    ('N', 'Nouvelle'),
    ('E', 'En cours'),
    ('T', 'Terminée'),
    ('A', 'Annulée'),
    ('R', 'Reportée'),
)

STATUT_ORDRE = (
    ('P', 'Planifié'),
    ('E', 'En cours'),
    ('T', 'Terminé'),
    ('A', 'Annulé'),
)

STATUT_RAPPORT = (
    ('S', 'Succès'),
    ('E', 'Échec'),
    ('R', 'Reporté'),
    ('N', 'Nécessite autre intervention'),
)

class DemandeIntervention(models.Model):
    panne = models.ForeignKey(Panne, on_delete=models.CASCADE, related_name='demandes')
    equipement = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='demandes')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    urgence = models.CharField(max_length=1, choices=[
        ('H', 'Haute'), 
        ('M', 'Moyenne'), 
        ('B', 'Basse')
    ], default='M')
    description = models.TextField()
    statut = models.CharField(max_length=1, choices=STATUT_DEMANDE, default='N')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Demande d'intervention"
        verbose_name_plural = "Demandes d'intervention"
    
    def __str__(self):
        return f"Demande #{self.id} - {self.equipement.code} - {self.panne.intitule}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('intervention:demande_detail', kwargs={'pk': self.pk})

class OrdreTravail(models.Model):
    demande = models.ForeignKey(DemandeIntervention, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordres')
    equipement = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='ordres')
    sous_ensemble = models.ForeignKey('equipments.SousEnsemble', on_delete=models.SET_NULL, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_planifiee = models.DateTimeField()
    date_debut = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    equipe = models.CharField(max_length=100)
    description = models.TextField()
    statut = models.CharField(max_length=1, choices=STATUT_ORDRE, default='P')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Ordre de travail"
        verbose_name_plural = "Ordres de travail"
    
    def __str__(self):
        return f"Ordre #{self.id} - {self.equipement.code}"
    
    def save(self, *args, **kwargs):
        if not self.demande and self.equipement.status != 'panne':
            self.equipement.status = 'panne'
            self.equipement.save()
        super().save(*args, **kwargs)

class RapportIntervention(models.Model):
    ordre = models.ForeignKey(OrdreTravail, on_delete=models.CASCADE, related_name='rapports')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    description = models.TextField()
    actions = models.TextField()
    pieces_utilisees = models.TextField(blank=True)
    temps_passe = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    statut = models.CharField(max_length=1, choices=STATUT_RAPPORT)
    created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True
)
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Rapport d'intervention"
        verbose_name_plural = "Rapports d'intervention"
    
    def __str__(self):
        return f"Rapport #{self.id} - {self.ordre}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Mise à jour du statut de la demande liée
        if self.ordre.demande:
            demande = self.ordre.demande
            if self.statut == 'S':
                demande.statut = 'T'
                # Si c'est un succès, on marque la panne comme résolue
                panne = demande.panne
                panne.resolue = True
                panne.save()
                # On vérifie si l'équipement peut repasser en statut "actif"
                if not demande.equipement.demandes.filter(statut__in=['N', 'E']).exists():
                    demande.equipement.status = 'actif'
                    demande.equipement.save()
            elif self.statut == 'R':
                demande.statut = 'R'
            elif self.statut == 'N':
                demande.statut = 'E'
            demande.save()