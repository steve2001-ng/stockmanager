from django.db import models
from django.utils import timezone
from equipments.models import Equipment 

class Panne(models.Model):
    NIVEAU_ALERTE_CHOICES = [
        ('faible', 'Faible'),
        ('moyen', 'Moyen'),
        ('eleve', 'Élevé'),
        ('critique', 'Critique'),
    ]
    
    intitule = models.CharField(max_length=200, verbose_name="Intitulé de la panne")
    niveau_alerte = models.CharField(
        max_length=10, 
        choices=NIVEAU_ALERTE_CHOICES, 
        default='moyen',
        verbose_name="Niveau d'alerte"
    )
    code_panne = models.CharField(max_length=20, unique=True, editable=False)
    emetteur = models.CharField(max_length=100, verbose_name="Nom de l'émetteur")
    equipement = models.ForeignKey(
        Equipment, 
        on_delete=models.CASCADE, 
        verbose_name="Équipement concerné"
    )
    site = models.CharField(max_length=100)
    date_heure_panne = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date et heure de la panne"
    )
    description = models.TextField(verbose_name="Description de la panne")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    resolue = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.code_panne:
            # Génération automatique du code panne (ex: PANNE-20230610-001)
            date_part = timezone.now().strftime('%Y%m%d')
            last_panne = Panne.objects.filter(code_panne__startswith=f'PANNE-{date_part}').order_by('code_panne').last()
            if last_panne:
                last_num = int(last_panne.code_panne.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.code_panne = f'PANNE-{date_part}-{new_num:03d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code_panne} - {self.intitule}"

    class Meta:
        verbose_name = "Panne"
        verbose_name_plural = "Pannes"
        ordering = ['-date_heure_panne']