from django.db import models
import uuid

class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icone = models.CharField(max_length=50, default='fa-box')  # Pour les icônes FontAwesome

    def __str__(self):
        return self.nom

    @classmethod
    def creer_categories_par_defaut(cls):
        defaults = [
            {"nom": "Composants électriques", "icone": "fa-bolt"},
            {"nom": "Composants frigorifiques", "icone": "fa-snowflake"},
            {"nom": "Fluide frigorigène", "icone": "fa-gas-pump"},
            {"nom": "Outillages", "icone": "fa-tools"}
        ]
        
        for item in defaults:
            cls.objects.get_or_create(
                nom=item['nom'],
                defaults={'icone': item['icone']}
            )

    '''def save(self, *args, **kwargs):
        # S'assure que les catégories existent lors du premier accès
        if not Categorie.objects.exists():
            Categorie.creer_categories_par_defaut()
        super().save(*args, **kwargs)'''

class Commande(models.Model):
    EN_ATTENTE = 'attente'
    VALIDEE = 'validee'
    REJETEE = 'rejetee'

    STATUS_CHOICES = [
        (EN_ATTENTE, 'En attente'),
        (VALIDEE, 'Validée'),
        (REJETEE, 'Rejetée'),
    ]


    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    designation = models.CharField(max_length=200)
    caracteristiques = models.TextField()
    quantite = models.IntegerField()
    objet = models.CharField(max_length=200)
    date = models.DateField(auto_now_add=True)
    initie_par = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=EN_ATTENTE)
    created_at = models.DateTimeField(auto_now_add=True)
    '''reference = models.CharField(
        max_length=10,
        unique=True,
        editable=False,
        blank=True  # Permet une valeur vide temporaire
    )'''
    
    class Meta:
        db_table = 'stockapp_commande'  # Optionnel - pour forcer le nom de table

    '''def save(self, *args, **kwargs):
        if not self.reference:
            # Génère une référence unique jusqu'à en trouver une disponible
            while True:
                new_ref = uuid.uuid4().hex[:8].upper()
                if not Commande.objects.filter(reference=new_ref).exists():
                    self.reference = new_ref
                    break
        super().save(*args, **kwargs)'''
    
    def __str__(self):
        return f"Commande #{self.id} - {self.designation}"

class Produit(models.Model):
    date_maj = models.DateTimeField(auto_now=True)  # Date de dernière modification
    code = models.CharField(max_length=20, unique=True, null=True, blank=True)    
    famille = models.CharField(max_length=50)
    designation = models.CharField(max_length=200)
    fournisseur = models.CharField(max_length=100)
    '''prix_unitaire = models.DecimalField(
        max_digits=12,  # Augmentez à 12 pour accommoder les valeurs en XAF
        decimal_places=0,  # 0 décimales pour le XAF
        verbose_name="PU (XAF)"
    )'''
    caracteristiques = models.TextField(
        blank=True,
        null=True,
        verbose_name="Caractéristiques techniques"
    )
    quantite = models.IntegerField(verbose_name="Qté en stock")
    stock_alerte = models.IntegerField()
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(
        upload_to='produits/',
        blank=True,
        null=True,
        verbose_name="Image du produit"
    )

    def __str__(self):
        return f"{self.code} - {self.designation}"
    
    class Meta:
        ordering = ['-date_maj']  # Tri par défaut par date descendante

    @property
    def statut_stock(self):
        if self.quantite <= self.stock_alerte:
            return "danger"
        elif self.quantite <= self.stock_alerte * 2:
            return "warning"
        return "success"

class MouvementStock(models.Model):
    ENTREE = 'entree'
    SORTIE = 'sortie'
    TYPE_CHOICES = [
        (ENTREE, 'Entrée'),
        (SORTIE, 'Sortie'),
    ]

    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantite = models.PositiveIntegerField()
    motif = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    effectue_par = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.get_type_display()} - {self.produit.designation} ({self.quantite})"
