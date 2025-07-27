# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import SiteEntrepot
from .forms import SiteEntrepotForm
from equipments.models import Equipment

def liste_sites(request):
    sites = SiteEntrepot.objects.all()
    site_id = request.GET.get('site')
    site_selectionne = SiteEntrepot.objects.filter(id=site_id).first() if site_id else None
    equipements = Equipment.objects.filter(site=site_selectionne.designation.lower()) if site_selectionne else []

    return render(request, 'entrepots/liste_sites.html', {
        'sites': sites,
        'site_selectionne': site_selectionne,
        'equipements': equipements,
    })

def ajouter_site(request):
    if request.method == 'POST':
        form = SiteEntrepotForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('entrepots:liste_sites')
    else:
        form = SiteEntrepotForm()
    return render(request, 'entrepots/ajouter_site.html', {'form': form})

def voir_site(request, pk):
    site = get_object_or_404(SiteEntrepot, pk=pk)
    return render(request, 'entrepots/voir_site.html', {'site': site})

def modifier_site(request, pk):
    site = get_object_or_404(SiteEntrepot, pk=pk)
    if request.method == 'POST':
        form = SiteEntrepotForm(request.POST, request.FILES, instance=site)
        if form.is_valid():
            form.save()
            return redirect('liste_sites')
    else:
        form = SiteEntrepotForm(instance=site)
    return render(request, 'entrepots/modifier_site.html', {'form': form, 'site': site})

def supprimer_site(request, pk):
    site = get_object_or_404(SiteEntrepot, pk=pk)
    if request.method == 'POST':
        site.delete()
        return redirect('entrepots:liste_sites')
    return render(request, 'entrepots/supprimer_site.html', {'site': site})
