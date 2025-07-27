from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, CustomUserChangeForm
from .models import CustomUser
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import Team
from .forms import TeamForm  # à créer

# Variables globales (à remplacer par un modèle en production)
ADMIN_PASSWORD = "admin"  # Mot de passe par défaut

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard_app:dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def admin_access(request):
    """Vue pour l'accès admin avec mot de passe simple"""
    if request.method == 'POST':
        password = request.POST.get('admin_password')
        if password == ADMIN_PASSWORD:
            request.session['admin_access'] = True
            return redirect('accounts:management')
        else:
            messages.error(request, "Mot de passe admin incorrect")
    return render(request, 'accounts/admin_access.html')

def check_admin_access(view_func):
    """Décorateur personnalisé pour vérifier l'accès admin"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_access'):
            return redirect('admin_access')
        return view_func(request, *args, **kwargs)
    return wrapper

@check_admin_access
def account_management(request):
    users = CustomUser.objects.all()
    return render(request, 'accounts/management.html', {'users': users})

@check_admin_access
def add_account(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Compte créé avec succès")
            return redirect('accounts:management')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/add.html', {'form': form})

@check_admin_access
def edit_account(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Compte mis à jour")
            return redirect('accounts:management')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'accounts/edit.html', {'form': form, 'user': user})

@check_admin_access
def delete_account(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Compte supprimé")
        return redirect('accounts:management')
    return render(request, 'accounts/delete.html', {'user': user})

@login_required
@check_admin_access
def change_admin_password(request):
    """Vue pour modifier le mot de passe admin"""
    global ADMIN_PASSWORD
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password == confirm_password:
            ADMIN_PASSWORD = new_password
            messages.success(request, "Mot de passe admin mis à jour")
            return redirect('accounts:management')
        else:
            messages.error(request, "Les mots de passe ne correspondent pas")
    
    return render(request, 'accounts/change_password.html')

@require_POST
@login_required
def toggle_admin_status(request, user_id):
    try:
        if not request.user.is_administrator:
            return JsonResponse({
                'success': False,
                'error': 'Permission denied'
            }, status=403)
        
        user = get_object_or_404(CustomUser, pk=user_id)
        data = json.loads(request.body.decode('utf-8'))  # Décode explicitement le body
        
        user.is_administrator = data.get('is_admin', False)
        user.save()
        
        return JsonResponse({'success': True})
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def team_list(request):
    teams = Team.objects.all()
    return render(request, 'accounts/team_list.html', {'teams': teams})

@login_required
def team_create(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:team_list')
    else:
        form = TeamForm()
    return render(request, 'accounts/team_form.html', {'form': form})

@login_required
def team_edit(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            return redirect('accounts:team_list')
    else:
        form = TeamForm(instance=team)
    return render(request, 'accounts/team_form.html', {
        'form': form,
        'edit': True,
        'team': team
    })

@login_required
def team_delete(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if request.method == 'POST':
        team.delete()
        return redirect('accounts:team_list')
    return render(request, 'accounts/team_confirm_delete.html', {
        'team': team
    })