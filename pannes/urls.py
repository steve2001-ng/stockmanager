from django.urls import path
from .views import ListePannesView, NouvellePanneView, ModifierPanneView, SupprimerPanneView
from . import views

app_name = 'pannes'

urlpatterns = [
    path('', ListePannesView.as_view(), name='liste_pannes'),
    path('nouvelle/', NouvellePanneView.as_view(), name='nouvelle_panne'),
    path('modifier/<int:pk>/', ModifierPanneView.as_view(), name='modifier_panne'),
    path('supprimer/<int:pk>/', SupprimerPanneView.as_view(), name='supprimer_panne'),
    path('export/pdf/', views.export_pannes_pdf, name='export_pannes_pdf'),
    path('failure-rates/', views.failure_rate_list, name='failure_rate_list'),
]