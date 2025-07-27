from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Count, Avg, F, ExpressionWrapper, fields, Sum, Q, DurationField
from datetime import timedelta, datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models.functions import TruncMonth 
from .models import DemandeIntervention, OrdreTravail, RapportIntervention
from .forms import DemandeInterventionForm, OrdreTravailForm, RapportInterventionForm
from equipments.models import Equipment, SousEnsemble
from pannes.models import Panne
from django.contrib import messages

class DemandeInterventionListView(LoginRequiredMixin, ListView):
    model = DemandeIntervention
    template_name = 'intervention/demande_list.html'
    context_object_name = 'demandes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('equipement', 'panne', 'created_by')
        statut = self.request.GET.get('statut')
        equipement = self.request.GET.get('equipement')
        site = self.request.GET.get('site')
        
        if statut:
            queryset = queryset.filter(statut=statut)
        if equipement:
            queryset = queryset.filter(equipement__code=equipement)
        if site:
            queryset = queryset.filter(equipement__site=site)
            
        return queryset.order_by('-date_creation')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipments'] = Equipment.objects.all().order_by('code')
        context['sites'] = Equipment.SITE_CHOICES
        return context

class DemandeInterventionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = DemandeIntervention
    form_class = DemandeInterventionForm
    template_name = 'intervention/demande_create.html'
    success_message = "Demande d'intervention créée avec succès"
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('intervention:demande_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pannes_non_resolues'] = Panne.objects.filter(resolue=False).select_related('equipement')
        return context

class DemandeInterventionDetailView(LoginRequiredMixin, DetailView):
    model = DemandeIntervention
    template_name = 'intervention/demande_detail.html'
    context_object_name = 'demande'

class DemandeInterventionUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = DemandeIntervention
    form_class = DemandeInterventionForm
    template_name = 'intervention/demande_update.html'
    success_message = "Demande d'intervention mise à jour avec succès"
    
    def get_success_url(self):
        return reverse_lazy('intervention:demande_detail', kwargs={'pk': self.object.pk})

class DemandeInterventionDeleteView(LoginRequiredMixin, DeleteView):
    model = DemandeIntervention
    template_name = 'intervention/demande_confirm_delete.html'
    success_url = reverse_lazy('intervention:demande_list')

class OrdreTravailListView(LoginRequiredMixin, ListView):
    model = OrdreTravail
    template_name = 'intervention/ordre_list.html'
    context_object_name = 'ordres'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('equipement', 'demande', 'sous_ensemble', 'created_by')
        statut = self.request.GET.get('statut')
        equipement = self.request.GET.get('equipement')
        site = self.request.GET.get('site')
        
        if statut:
            queryset = queryset.filter(statut=statut)
        if equipement:
            queryset = queryset.filter(equipement__code=equipement)
        if site:
            queryset = queryset.filter(equipement__site=site)
            
        return queryset.order_by('-date_creation')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipments'] = Equipment.objects.all().order_by('code')
        context['sites'] = Equipment.SITE_CHOICES
        return context

class OrdreTravailCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = OrdreTravail
    form_class = OrdreTravailForm
    template_name = 'intervention/ordre_create.html'
    success_message = "Ordre de travail créé avec succès"
    
    def get_initial(self):
        initial = super().get_initial()
        demande_id = self.request.GET.get('demande')
        if demande_id:
            demande = get_object_or_404(DemandeIntervention, pk=demande_id)
            initial['demande'] = demande
            initial['equipement'] = demande.equipement
        return initial
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('intervention:ordre_detail', kwargs={'pk': self.object.pk})

class OrdreTravailDetailView(LoginRequiredMixin, DetailView):
    model = OrdreTravail
    template_name = 'intervention/ordre_detail.html'
    context_object_name = 'ordre'

class OrdreTravailUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = OrdreTravail
    form_class = OrdreTravailForm
    template_name = 'intervention/ordre_update.html'
    success_message = "Ordre de travail mis à jour avec succès"
    
    def get_success_url(self):
        return reverse_lazy('intervention:ordre_detail', kwargs={'pk': self.object.pk})

class RapportInterventionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = RapportIntervention
    form_class = RapportInterventionForm
    template_name = 'intervention/rapport_create.html'
    success_message = "Rapport d'intervention créé avec succès"
    
    def get_initial(self):
        initial = super().get_initial()
        ordre_id = self.request.GET.get('ordre')
        if ordre_id:
            ordre = get_object_or_404(OrdreTravail, pk=ordre_id)
            initial['ordre'] = ordre
        return initial
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        ordre = form.instance.ordre
        ordre.statut = 'T'
        ordre.date_fin = timezone.now()
        ordre.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('intervention:rapport_pdf', kwargs={'pk': self.object.pk})

def generate_rapport_pdf(request, pk):
    rapport = get_object_or_404(RapportIntervention, pk=pk)
    template_path = 'intervention/rapport_detail.html'
    context = {'rapport': rapport}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="rapport_intervention_{pk}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF')
    return response

def stats_equipement(request):
    # 1) Liste de tous les équipements pour le menu déroulant
    equipements = Equipment.objects.order_by('designation')

    # 2) Récupération brute du paramètre (peut être None ou chaîne vide)
    raw_equip_id = request.GET.get('equip_id', None)

    # -- Cas A : pas de paramètre du tout → affichage simple de la sélection
    if raw_equip_id is None:
        return render(request, 'intervention/stats_equipement.html', {
            'equipements': equipements,
            'equipement': None,
        })

    # 3) L’utilisateur a cliqué sur “Afficher” :
    equip_id = raw_equip_id.strip()
    # -- Cas B : paramètre présent mais vide → on redirige et on affiche l’erreur
    if equip_id == '':
        messages.error(request, "Veuillez sélectionner un équipement.")
        return redirect('intervention:stats_equipement')

    # 4) Chargement de l’équipement (sera toujours non vide ici)
    equipement = get_object_or_404(Equipment, pk=equip_id)

    # 5) Définition de la période (12 derniers mois par défaut)
    end_date = timezone.now()
    start_date = end_date - relativedelta(months=12)
    if request.GET.get('start_date') and request.GET.get('end_date'):
        try:
            start_date = datetime.strptime(request.GET['start_date'], '%Y-%m-%d')
            end_date   = datetime.strptime(request.GET['end_date'], '%Y-%m-%d')
        except ValueError:
            pass

    # 6) Filtrage des rapports
    rapports = RapportIntervention.objects.filter(
        ordre__equipement=equipement,
        ordre__date_fin__range=(start_date, end_date)
    ).select_related('ordre')

    # 7) Calcul du MTTR
    mttr_agg = rapports.annotate(
        duree=ExpressionWrapper(
            F('ordre__date_fin') - F('ordre__date_debut'),
            output_field=DurationField()
        )
    ).aggregate(avg_duree=Avg('duree'))
    mttr = mttr_agg['avg_duree'] or timedelta(0)

    # 8) Calcul du MTBF
    pannes = Panne.objects.filter(
        equipement=equipement,
        resolue=True,
        date_heure_panne__range=(start_date, end_date)
    ).order_by('date_heure_panne')
    mtbf = None
    if pannes.count() > 1:
        diffs = [
            (pannes[i].date_heure_panne - pannes[i-1].date_heure_panne).total_seconds()
            for i in range(1, pannes.count())
        ]
        avg_sec = sum(diffs) / len(diffs)
        mtbf = timedelta(seconds=avg_sec)

    # Décomposition MTBF
    if mtbf:
        mtbf_days = mtbf.days
        mtbf_hours = int(mtbf.seconds / 3600)
    else:
        mtbf_days = mtbf_hours = None

    # 9) Disponibilité
    total_h = (end_date - start_date).total_seconds() / 3600
    indispo_h = sum(
        (r.ordre.date_fin - r.ordre.date_debut).total_seconds() / 3600
        for r in rapports if r.ordre.date_debut and r.ordre.date_fin
    )
    dispo_pct = ((total_h - indispo_h) / total_h * 100) if total_h > 0 else 100

    # 10) Statuts pour le graphique
    count_S = rapports.filter(statut='S').count()
    count_E = rapports.filter(statut='E').count()
    count_R = rapports.filter(statut='R').count()
    total   = rapports.count()
    count_O = total - (count_S + count_E + count_R)

    return render(request, 'intervention/stats_equipement.html', {
        'equipements':       equipements,
        'equipement':        equipement,
        'start_date':        start_date,
        'end_date':          end_date,
        'mttr':              mttr,
        'mtbf':              mtbf,
        'mtbf_days':         mtbf_days,
        'mtbf_hours':        mtbf_hours,
        'disponibilite':     round(dispo_pct, 2),
        'rapports':          rapports,
        'rapports_reussis':  count_S,
        'rapports_echoues':  count_E,
        'rapports_reportes': count_R,
        'rapports_autres':   count_O,
    })

def stats_interventions(request):
    # Période par défaut : 12 derniers mois
    end_date = timezone.now()
    start_date = end_date - relativedelta(months=12)
    
    # Filtrage par période si spécifié
    if request.GET.get('start_date') and request.GET.get('end_date'):
        try:
            start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d')
        except ValueError:
            pass
    
    # Performance des interventions
    demandes = DemandeIntervention.objects.filter(
        date_creation__range=(start_date, end_date)
    ).select_related('equipement')
    
    ordres = OrdreTravail.objects.filter(
        date_creation__range=(start_date, end_date)
    ).select_related('equipement')
    
    rapports = RapportIntervention.objects.filter(
        date_creation__range=(start_date, end_date)
    ).select_related('ordre', 'ordre__equipement')
    
    # Statistiques par site
    stats_site = (
        demandes.values('equipement__site')
        .annotate(
            count=Count('id'),
            completed=Count('id', filter=Q(statut='T')),
            in_progress=Count('id', filter=Q(statut='E')),
            new=Count('id', filter=Q(statut='N'))
        )
        .order_by('-count')
    )
    
    # Évolution mensuelle
    monthly_data = (
        demandes.annotate(month=TruncMonth('date_creation'))
        .values('month')
        .annotate(
            count=Count('id'),
            completed=Count('id', filter=Q(statut='T')),
            mttr=Avg(
                ExpressionWrapper(
                    F('ordres__rapports__ordre__date_fin') - F('ordres__rapports__ordre__date_debut'),
                    output_field=fields.DurationField()
                ),
                filter=Q(ordres__rapports__statut='S')
            )
        )
        .order_by('month')
    )
    
    stats = {
        'total_demandes': demandes.count(),
        'demandes_par_statut': demandes.values('statut').annotate(count=Count('id')),
        'total_ordres': ordres.count(),
        'ordres_par_statut': ordres.values('statut').annotate(count=Count('id')),
        'total_rapports': rapports.count(),
        'rapports_par_statut': rapports.values('statut').annotate(count=Count('id')),
        'stats_site': stats_site,
        'monthly_data': list(monthly_data),
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
    }
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'monthly_data': stats['monthly_data'],
            'stats_site': list(stats['stats_site']),
        })
    
    return render(request, 'intervention/stats_interventions.html', {'stats': stats})

def get_equipment_stats(request, equipment_id):
    equipement = get_object_or_404(Equipment, pk=equipment_id)
    
    # Calcul des indicateurs
    rapports = RapportIntervention.objects.filter(ordre__equipement=equipement)
    
    # MTTR
    mttr = rapports.annotate(
        duree=ExpressionWrapper(F('ordre__date_fin') - F('ordre__date_debut'), 
        output_field=fields.DurationField())
    ).aggregate(avg_duree=Avg('duree'))['avg_duree'] or timedelta(0)
    
    # Nombre d'interventions
    interventions_count = rapports.count()
    
    # Taux de réussite
    success_rate = (rapports.filter(statut='S').count() / interventions_count * 100) if interventions_count > 0 else 0
    
    data = {
        'mttr': str(mttr),
        'interventions_count': interventions_count,
        'success_rate': round(success_rate, 2),
        'equipment_name': equipement.designation,
    }
    
    return JsonResponse(data)

def get_panne_details(request, panne_id):
    try:
        panne = Panne.objects.get(pk=panne_id)
        equipement = panne.equipement
        return JsonResponse({
            'equipement_id': equipement.id,
            'equipement_code': equipement.code,
            'equipement_designation': equipement.designation,
            'equipement_site': equipement.get_site_display()
        })
    except Panne.DoesNotExist:
        return JsonResponse({'error': 'Panne non trouvée'}, status=404)