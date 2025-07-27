from django.shortcuts import render, redirect, get_object_or_404
from .models import ElectricityConsumption
from .forms import ElectricityConsumptionForm
from entrepots.models import SiteEntrepot
from django.utils.dateformat import format
from django.urls import reverse

def consommation_par_site(request):
    sites = SiteEntrepot.objects.all()
    site_id = request.GET.get('site')
    site_selectionne = SiteEntrepot.objects.filter(id=site_id).first() if site_id else None

    consommations = []
    labels = []
    values = []

    if site_selectionne:
        consommations = ElectricityConsumption.objects.filter(site=site_selectionne).order_by('mois')
        labels = [format(c.mois, 'F Y') for c in consommations]
        values = [float(c.montant) for c in consommations]

    form = ElectricityConsumptionForm()

    if request.method == 'POST':
        form = ElectricityConsumptionForm(request.POST)
        if form.is_valid():
            conso = form.save(commit=False)
            conso.site = site_selectionne
            conso.save()
            return redirect(f"{request.path}?site={site_selectionne.id}")

    return render(request, 'consommation/consommation_par_site.html', {
        'sites': sites,
        'site_selectionne': site_selectionne,
        'form': form,
        'consommations': consommations,
        'labels': labels,
        'values': values,
    })

def modifier_consommation(request, pk):
    conso = get_object_or_404(ElectricityConsumption, pk=pk)
    form = ElectricityConsumptionForm(instance=conso)

    if request.method == 'POST':
        form = ElectricityConsumptionForm(request.POST, instance=conso)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('consommation:consommation_par_site')}?site={conso.site.id}")

    return render(request, 'consommation/modifier_consommation.html', {
        'form': form,
        'conso': conso,
    })

def supprimer_consommation(request, pk):
    conso = get_object_or_404(ElectricityConsumption, pk=pk)
    site_id = conso.site.id
    conso.delete()
    return redirect(f"{reverse('consommation:consommation_par_site')}?site={site_id}")
