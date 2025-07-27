from django.urls import path
from . import views

app_name = 'equipments'

urlpatterns = [
    path('', views.EquipmentListView.as_view(), name='equipment_list'),
    path('new/', views.equipment_create, name='equipment_create'),
    path('<str:pk>/edit/', views.equipment_update, name='equipment_update'),
    path('<str:code>/arbre/', views.equipment_tree_html, name='equipment_tree_html'),
    path('sous-ensemble/<int:pk>/', views.gestion_sous_ensemble, name='sous_ensemble_edit'),
    path('sous-ensemble/new/<str:equipement_pk>/', views.gestion_sous_ensemble, name='sous_ensemble_create'),
    path('delete/<str:pk>/', views.equipment_delete, name='equipment_delete'),
    path('sous-ensemble/<int:pk>/delete/', views.sous_ensemble_delete, name='sous_ensemble_delete'),
    path('<str:code>/arborescence/', views.get_arborescence_view, name='arborescence'),
    path('<str:code>/', views.equipment_detail, name='equipment_detail'),

]