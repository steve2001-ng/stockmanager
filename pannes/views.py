from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from .models import Panne
from .forms import PanneForm, FailureRateFilterForm
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from equipments.models import Equipment
from django.contrib.auth.decorators import login_required
import math


class ListePannesView(ListView):
    model = Panne
    template_name = 'pannes/liste_pannes.html'
    context_object_name = 'pannes'
    paginate_by = 10

    def get_queryset(self):
        period = self.request.GET.get('period', 'all')
        queryset = Panne.objects.all()
        
        today = timezone.now().date()
        
        if period == 'today':
            queryset = queryset.filter(date_heure_panne__date=today)
        elif period == 'week':
            start_week = today - timedelta(days=today.weekday())
            queryset = queryset.filter(date_heure_panne__date__gte=start_week)
        elif period == 'month':
            queryset = queryset.filter(date_heure_panne__month=today.month, 
                                     date_heure_panne__year=today.year)
        
        return queryset.order_by('-date_heure_panne')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Comptage des pannes par période
        context['count_all'] = Panne.objects.count()
        context['count_today'] = Panne.objects.filter(date_heure_panne__date=today).count()
        context['count_week'] = Panne.objects.filter(
            date_heure_panne__date__gte=today - timedelta(days=today.weekday())
        ).count()
        context['count_month'] = Panne.objects.filter(
            date_heure_panne__month=today.month,
            date_heure_panne__year=today.year
        ).count()
        context['active_period'] = self.request.GET.get('period', 'all')
        
        return context
    
class NouvellePanneView(SuccessMessageMixin, CreateView):
    model = Panne
    form_class = PanneForm
    template_name = 'pannes/nouvelle_panne.html'
    success_url = reverse_lazy('pannes:liste_pannes')
    success_message = "La panne a été enregistrée avec succès!"

class ModifierPanneView(SuccessMessageMixin, UpdateView):
    model = Panne
    form_class = PanneForm
    template_name = 'pannes/modifier_panne.html'
    success_url = reverse_lazy('pannes:liste_pannes')
    success_message = "La panne a été modifiée avec succès!"

class SupprimerPanneView(DeleteView):
    model = Panne
    template_name = 'pannes/supprimer_panne.html'
    success_url = reverse_lazy('pannes:liste_pannes')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "La panne a été supprimée avec succès!")
        return super().delete(request, *args, **kwargs)

def export_pannes_pdf(request):
    # Récupère le même queryset que dans ta ListView
    period = request.GET.get('period', 'all')
    qs = Panne.objects.all()
    if period == 'today':
        qs = qs.filter(date_creation__date=timezone.now().date())
    elif period == 'week':
        start = timezone.now().date() - timedelta(days=7)
        qs = qs.filter(date_creation__date__gte=start)
    elif period == 'month':
        start = timezone.now().date().replace(day=1)
        qs = qs.filter(date_creation__date__gte=start)

    # Contexte pour le PDF
    context = {
        'pannes': qs,
        'period': period,
        'generated_on': timezone.now(),
    }

    # Génère le HTML à partir d’un template dédié
    template = get_template('pannes/pannes_pdf.html')
    html = template.render(context)

    # Crée la réponse PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="pannes.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération PDF')
    return response

@login_required
def failure_rate_list(request):
    form   = FailureRateFilterForm(request.GET or None)
    period = form['period'].value() or 'month'
    q      = request.GET.get('q', '').strip()

    # On prépare le QuerySet
    equipments = Equipment.objects.all()

    if q:
        # 1) Recherche sur la désignation
        qs = Q(designation__icontains=q)

        # 2) Recherche sur le label du site (choices)
        #    On construit la liste des codes dont le label contient q
        matching_codes = [
            code for code, label in Equipment.SITE_CHOICES
            if q.lower() in label.lower()
        ]
        if matching_codes:
            qs |= Q(site__in=matching_codes)

        # Applique le filtre
        equipments = equipments.filter(qs)

    # Calcul des taux / MTBF…
    rates = []

    # Durée t en jours selon la période
    period_days = {'week': 7, 'month': 30, 'year': 365}.get(period, 30)

    for eq in equipments:
        λ = eq.failure_rate(period=period)
        mtbf = (1.0 / λ) if λ else None
        reliability = None
        if λ:
            reliability = math.exp(-λ * period_days)

        rates.append({'equipment': eq, 'rate': λ, 'mtbf': mtbf, 'reliability': reliability})

    return render(request, 'pannes/failure_rates.html', {
        'form':   form,
        'rates':  rates,
        'period': period,
        'q':      q,
    })