# urls.py
from django.urls import path
from . import views

app_name = 'entrepots'

urlpatterns = [
    path('', views.liste_sites, name='liste_sites'),
    path('ajouter/', views.ajouter_site, name='ajouter_site'),
    path('<int:pk>/voir/', views.voir_site, name='voir_site'),
    path('<int:pk>/modifier/', views.modifier_site, name='modifier_site'),
    path('<int:pk>/supprimer/', views.supprimer_site, name='supprimer_site'),
]
