from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # URLs d'authentification (corrigées)
    path('login/', views.login_view, name='login'),  # Maintenant accessible via /comptes/login/
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),

    # URLs de gestion CRUD
    path('management/', views.account_management, name='management'),
    path('add/', views.add_account, name='add'),
    path('edit/<int:user_id>/', views.edit_account, name='edit'),
    path('delete/<int:user_id>/', views.delete_account, name='delete'),
    path('admin-access/', views.admin_access, name='admin_access'),
    path('change-password/', views.change_admin_password, name='change_password'),
    path('toggle-admin/<int:user_id>/', views.toggle_admin_status, name='toggle_admin'),
    path('teams/', views.team_list, name='team_list'),
    path('teams/create/', views.team_create, name='team_create'),
    path('teams/<int:pk>/edit/',   views.team_edit,   name='team_edit'),
    path('teams/<int:pk>/delete/', views.team_delete, name='team_delete'),
]