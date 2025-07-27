from django.urls import path
from . import views

app_name = 'stockapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('categories/', views.categories, name='categories'),
    path('categorie/<int:categorie_id>/produits/', views.produits_par_categorie, name='produits_categorie'),
    path('produit/<int:pk>/modifier/', views.modifier_produit, name='modifier_produit'),
    path('produit/<int:pk>/supprimer/', views.supprimer_produit, name='supprimer_produit'),
    path('categorie/<int:categorie_id>/commandes/creer/', views.creer_commande, name='creer_commande'),
    path('categorie/<int:categorie_id>/commandes/historique/', 
         views.historique_commandes, 
         name='historique_commandes'),
    path('produits/alerte/', views.produits_alerte, name='produits_alerte'),
    path('commandes/historique/', views.historique_commandes_all, name='historique_commandes_all'),
    path('commande/<int:commande_id>/valider/', views.valider_commande, name='valider_commande'),
    path('commande/<int:commande_id>/rejeter/', views.rejeter_commande, name='rejeter_commande'),
    path('categorie/<int:categorie_id>/mouvements/', views.historique_mouvements, name='historique_mouvements'),
    path('commande/<int:commande_id>/pdf/', views.commande_pdf, name='commande_pdf'),
    path('categorie/<int:categorie_id>/commandes/pdf/', views.historique_commandes_pdf, name='historique_commandes_pdf'),
    path('categorie/<int:categorie_id>/mouvements/pdf/', views.historique_mouvements_pdf, name='historique_mouvements_pdf'),
    path('api/produit-stock/<int:pk>/', views.produit_stock, name='produit_stock'),

]