from django.db import models


class SiteEntrepot(models.Model):
    designation = models.CharField(max_length=255)
    ville = models.CharField(max_length=100)
    localisation = models.CharField(max_length=255)
    responsable = models.CharField(max_length=100)
    capacite_totale = models.PositiveIntegerField()
    photo = models.ImageField(upload_to='sites_photos/')
    documentation = models.FileField(upload_to='sites_docs/', blank=True, null=True)  # 👈


    def __str__(self):
        return self.designation


