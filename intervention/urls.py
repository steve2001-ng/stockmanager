from django.urls import path
from . import views

app_name = 'intervention'

urlpatterns = [
    # Demandes d'intervention
    path('demandes/', views.DemandeInterventionListView.as_view(), name='demande_list'),
    path('demandes/ajouter/', views.DemandeInterventionCreateView.as_view(), name='demande_create'),
    path('demandes/<int:pk>/', views.DemandeInterventionDetailView.as_view(), name='demande_detail'),
    path('demandes/<int:pk>/modifier/', views.DemandeInterventionUpdateView.as_view(), name='demande_update'),
    path('demandes/<int:pk>/supprimer/', views.DemandeInterventionDeleteView.as_view(), name='demande_delete'),
    
    # Ordres de travail
    path('ordres/', views.OrdreTravailListView.as_view(), name='ordre_list'),
    path('ordres/ajouter/', views.OrdreTravailCreateView.as_view(), name='ordre_create'),
    path('ordres/<int:pk>/', views.OrdreTravailDetailView.as_view(), name='ordre_detail'),
    path('ordres/<int:pk>/modifier/', views.OrdreTravailUpdateView.as_view(), name='ordre_update'),
    
    # Rapports d'intervention
    path('rapports/ajouter/', views.RapportInterventionCreateView.as_view(), name='rapport_create'),
    path('rapports/<int:pk>/pdf/', views.generate_rapport_pdf, name='rapport_pdf'),
    
    # Statistiques
    path('stats/equipement/', views.stats_equipement, name='stats_equipement'),
    path('stats/interventions/', views.stats_interventions, name='stats_interventions'),
    path('api/stats/equipement/<int:equipment_id>/', views.get_equipment_stats, name='api_equipment_stats'),
    path('api/get-panne-details/<int:panne_id>/', views.get_panne_details, name='get_panne_details'),
]