from django.urls import path
from . import views

app_name = 'consommation'
 
urlpatterns = [
    path('', views.consommation_par_site, name='consommation_par_site'),
    path('modifier/<int:pk>/', views.modifier_consommation, name='modifier_consommation'),
    path('supprimer/<int:pk>/', views.supprimer_consommation, name='supprimer_consommation'),
]
