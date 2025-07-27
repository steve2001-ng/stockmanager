from django.urls import path
from . import views

app_name = 'messagerie'

urlpatterns = [
    path('', views.message_list,   name='message_list'),
    path('new/', views.message_create, name='message_create'),
    path('<int:pk>/', views.message_detail, name='message_detail'),
    path('<int:pk>/edit/',   views.message_edit,   name='message_edit'),
    path('<int:pk>/delete/', views.message_delete, name='message_delete'),
]
