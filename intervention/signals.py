from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import DemandeIntervention, RapportIntervention
from pannes.models import Panne
from equipments.models import Equipment

@receiver(post_save, sender=DemandeIntervention)
def update_equipment_status_on_demande(sender, instance, created, **kwargs):
    if created and instance.equipement.status != 'panne':
        instance.equipement.status = 'panne'
        instance.equipement.save()

@receiver(post_save, sender=RapportIntervention)
def update_panne_status_on_rapport(sender, instance, **kwargs):
    if instance.statut == 'S' and instance.ordre.demande:
        panne = instance.ordre.demande.panne
        panne.resolue = True
        panne.save()
        
        # Vérifier si l'équipement peut revenir à "actif"
        equipement = instance.ordre.equipement
        if not equipement.demandes.filter(statut__in=['N', 'E']).exists():
            equipement.status = 'actif'
            equipement.save()