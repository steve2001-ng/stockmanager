from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from .models import Equipment, SousEnsemble
from .forms import EquipmentForm, SousEnsembleForm
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST

class EquipmentListView(ListView):
    model = Equipment
    template_name = 'equipments/equipment_list.html'
    context_object_name = 'equipments'
    
    def get_queryset(self):
        family = self.request.GET.get('family')
        if family:
            return Equipment.objects.filter(family=family)
        return Equipment.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_family'] = self.request.GET.get('family', '')
        return context

def equipment_create(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                equipment = form.save()
                messages.success(request, f"Équipement {equipment.code} enregistré!")
                return redirect('equipments:equipment_list')
            except Exception as e:
                messages.error(request, f"Erreur: {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = EquipmentForm()
    
    equipments = Equipment.objects.all()

    return render(request, 'equipments/equipment_form.html', {
        'form': form,
        'equipments': equipments,  
    })


def equipment_update(request, pk):
    equipment = get_object_or_404(Equipment, code=pk)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES, instance=equipment)
        if form.is_valid():
            form.save()
            return redirect('equipments:equipment_list')
    else:
        form = EquipmentForm(instance=equipment)
    return render(request, 'equipments/equipment_form.html', {'form': form})

def equipment_delete(request, pk):
    equipment = get_object_or_404(Equipment, code=pk)
    if request.method == 'POST':
        equipment.delete()
        messages.success(request, f"Équipement {pk} supprimé.")
        return redirect('equipments:equipment_list')
    return render(request, 'equipments/equipment_confirm_delete.html', {'equipment': equipment})

'''def arborescence_equipement(request, pk):
    equipement = get_object_or_404(Equipment, code=pk)
    racines = SousEnsemble.objects.filter(equipement=equipement, parent__isnull=True)
    
    data = {
        'equipement': {
            'code': equipement.code,
            'designation': equipement.designation
        },
        'arborescence': [s.get_arborescence() for s in racines]
    }
    return JsonResponse(data)'''

def gestion_sous_ensemble(request, pk=None, equipement_pk=None):
    parent_id = request.GET.get("parent")

    if pk:
        instance = get_object_or_404(SousEnsemble, pk=pk)
        equipement = instance.equipement
    else:
        instance = None
        equipement = get_object_or_404(Equipment, pk=equipement_pk)

    if request.method == 'POST':
        form = SousEnsembleForm(request.POST, request.FILES, instance=instance, equipement=equipement)
        if form.is_valid():
            sous_ensemble = form.save(commit=False)
            sous_ensemble.equipement = equipement

            if not sous_ensemble.parent and parent_id:
                try:
                    sous_ensemble.parent = SousEnsemble.objects.get(id=parent_id, equipement=equipement)
                except SousEnsemble.DoesNotExist:
                    pass

            sous_ensemble.save()
            messages.success(request, "Sous-ensemble enregistré avec succès!")
            return redirect('equipments:equipment_detail', code=equipement.code)
        messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = SousEnsembleForm(instance=instance, equipement=equipement)
        if parent_id:
            try:
                form.fields['parent'].initial = SousEnsemble.objects.get(id=parent_id, equipement=equipement)
            except SousEnsemble.DoesNotExist:
                pass

    return render(request, 'equipments/sous_ensemble_form.html', {
        'form': form,
        'equipement': equipement,
        'editing': pk is not None
    })

def sous_ensemble_delete(request, pk):
    sous_ensemble = get_object_or_404(SousEnsemble, pk=pk)
    equipement_code = sous_ensemble.equipement.code
    
    if request.method == 'POST':
        sous_ensemble.delete()
        messages.success(request, 'Sous-ensemble supprimé avec succès')
        return redirect('equipments:equipment_detail', code=equipement_code)

    return render(request, 'equipments/sous_ensemble_confirm_delete.html', {
        'sous_ensemble': sous_ensemble
    })

def get_arborescence_view(request, code):
    equipment = get_object_or_404(Equipment, code=code)
    racines = SousEnsemble.objects.filter(equipement=equipment, parent__isnull=True)

    arbo = [r.get_arborescence() for r in racines]
    return JsonResponse({
        'equipement': {
            'code': equipment.code,
            'designation': equipment.designation,
        },
        'arborescence': arbo
    })


def equipment_detail(request, code):
    equipment = get_object_or_404(Equipment, code=code)
    return render(request, 'equipments/equipment_detail.html', {
        'equipment': equipment,
        'title': f"Détails - {equipment.code}"
    })

def equipment_tree_html(request, code):
    equipment = get_object_or_404(Equipment, code=code)
    racines = SousEnsemble.objects.filter(equipement=equipment, parent__isnull=True)
    arbo = [r.get_arborescence() for r in racines]
    
    return render(request, 'equipments/equipment_tree.html', {
        'equipement': equipment,
        'arborescence': arbo
    })
