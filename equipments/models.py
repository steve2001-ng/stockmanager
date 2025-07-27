from django.db import models
from django.urls import reverse

class Equipment(models.Model):
    FAMILY_CHOICES = [
        ('CF', 'Chambre Froide'),
        ('CG', 'Congélateur'),
    ]
    
    STATUS_CHOICES = [
        ('actif', 'Actif'),
        ('panne', 'En panne'),
        ('arret', 'Arrêt'),
    ]
    SITE_CHOICES = [
        ('digue', 'DIGUE'),
        ('cittma', 'CITTMA'),
        ('sotranav', 'SOTRANAV'),
        ('E1', 'ESSENGUE 1'),
        ('E2', 'ESSENGUE 2'),
        ('E3', 'ESSENGUE 3'),
        ('E4', 'ESSENGUE 4'),
        ('E5', 'ESSENGUE 5'),
        ('E6', 'ESSENGUE 6'),
        ('bonaberi', 'BONABERI'),
    ]
    
    family = models.CharField(max_length=2, choices=FAMILY_CHOICES, verbose_name="Famille")
    sub_family = models.CharField(max_length=100, verbose_name="Sous-famille")
    code = models.CharField(max_length=50, primary_key=True, verbose_name="Code")
    designation = models.CharField(max_length=200, verbose_name="Désignation")
    capacity = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Capacité (T)")
    site = models.CharField(max_length=100, choices=SITE_CHOICES, verbose_name="Site")    
    number = models.CharField(max_length=50, verbose_name="Numéro")
    group_count = models.IntegerField(verbose_name="Nombre de groupes")
    power_per_group = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Puissance/groupe (kW)")
    manufacturer = models.CharField(max_length=100, verbose_name="Constructeur")
    temperature_setpoint = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="T° consigne")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name="Statut")
    commissioning_date = models.DateField(verbose_name="Date de mise en service")
    documentation = models.FileField(upload_to='equipments/docs/', blank=True, null=True, verbose_name="Documentation")
    
    class Meta:
        ordering = ['family', 'code']
        verbose_name = "Équipement"
        verbose_name_plural = "Équipements"
    
    def __str__(self):
        return f"{self.get_family_display()} - {self.code} - {self.designation}"
    
    def get_absolute_url(self):
        return reverse('equipments:equipment_detail', kwargs={'code': self.code})
    
    def failure_rate(self, period='month'):
        """
        Calcule λ = nombre de pannes / nombre de jours de la période choisie.
        period: 'week' (7 jours), 'month' (30 jours) ou 'year' (365 jours)
        Retourne un float (pannes/jour).
        """
        from django.utils import timezone
        from pannes.models import Panne
        import datetime

        now = timezone.now()
        # Choix de la durée selon la période
        if period == 'week':
            delta = datetime.timedelta(weeks=1)
        elif period == 'year':
            delta = datetime.timedelta(days=365)
        else:
            delta = datetime.timedelta(days=30)

        start = now - delta
        # filtre sur la FK 'equipement' et le champ 'date_heure_panne'
        count = Panne.objects.filter(
            equipement=self,
            date_heure_panne__gte=start
        ).count()

        days = delta.days or 1
        return count / days

class SousEnsemble(models.Model):
    TYPE_CHOICES = [
        ('COND', 'Groupe de condensation'),
        ('EVAP', 'Groupe d\'évaporation'),
        ('COMP', 'Compresseur'),
        ('DET', 'Détendeur'),
        ('PRESSHP', 'Pressostat HP'),
        ('PRESSBP', 'Pressostat BP'),
        ('PRESSHL', 'Pressostat Huile'),
        ('VAN', 'Electrovanne'),
        ('BACL', 'Bouteille anti CL'),
        ('RESERVOIR', 'Réservoir de liquide'),
        ('FILTREDES', 'Filtre déshydrateur'),
        ('VOY', 'Voyant'),
        ('OILSEP', 'Séparateur d\'huile'),
        ('VENTILO', 'Ventilateur'),
        ('CAPACITOR', 'Condensateur'),
        ('RESISTANCE', 'Résistance chauffante'),
        ('PANNEAU', 'Panneau d\'isolation'),
        ('LUMI', 'Luminaire'),
        ('RIDAIR', 'Rideau d\'air'),
        ('RIDLAN', 'Rideau à lanière'),

    ]
    
    equipement = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='sous_ensembles')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='enfants')
    type = models.CharField(max_length=12, choices=TYPE_CHOICES)
    code = models.CharField(max_length=50)
    designation = models.CharField(max_length=200)
    caracteristiques = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='equipments/images/', blank=True, null=True, verbose_name="Image")

    
    class Meta:
        ordering = ['type', 'code']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.code}"
    
    def get_arborescence(self):
        """Retourne l'arborescence complète à partir de ce nœud"""
        return {
            'id': self.id,
            'type': self.get_type_display(),
            'code': self.code,
            'designation': self.designation,
            'caracteristiques': self.caracteristiques if self.caracteristiques else "",
            'image_url': self.image.url if self.image else None,
            'enfants': [enfant.get_arborescence() for enfant in self.enfants.all()]
        }

