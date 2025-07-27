from django.contrib import admin
from .models import Categorie, Produit

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'icone')
    search_fields = ('nom',)

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('date_maj','code', 'designation', 'caracteristiques', 'quantite', 'categorie', 'statut_stock')
    readonly_fields = ('date_maj',)
    list_filter = ('categorie', 'famille')
    search_fields = ('date_maj','code', 'designation', 'fournisseur')
    
    def statut_stock(self, obj):
        return obj.statut_stock.upper()
    statut_stock.short_description = 'Statut'