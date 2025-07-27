from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from .models import TemperatureReading, PreventiveTask
from .forms import TemperatureReadingForm, PreventiveTaskForm
from django.shortcuts import render
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect


class TemperatureReadingListView(ListView):
    model = TemperatureReading
    template_name = 'preventive/temperature_readings.html'
    context_object_name = 'readings'

    def get_queryset(self):
        return TemperatureReading.objects.select_related('equipment').order_by('-reading_date')

class TemperatureReadingCreateView(CreateView):
    model = TemperatureReading
    form_class = TemperatureReadingForm
    template_name = 'preventive/temperature_reading_form.html'
    success_url = reverse_lazy('preventive:temperature_readings')
    
    def form_valid(self, form):
        # Pour debug - affiche les données du formulaire dans la console
        print("Données du formulaire:", form.cleaned_data)
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Vérifiez le queryset dans le contexte
        equipments = context['form'].fields['equipment'].queryset
        print("Équipements dans le contexte:", list(equipments))
        return context

class PreventiveTaskListView(ListView):
    model = PreventiveTask
    template_name = 'preventive/calendar.html'
    context_object_name = 'tasks'

class PreventiveTaskCalendarView(ListView):
    model = PreventiveTask
    template_name = 'preventive/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Gestion de la période affichée
        date_str = self.request.GET.get('date')
        if date_str:
            current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            current_date = timezone.now().date()
            
        start_date = current_date - timedelta(days=current_date.weekday())
        end_date = start_date + timedelta(days=6)
        
        # Préparation des données pour le calendrier
        days = []
        for i in range(7):
            day = start_date + timedelta(days=i)
            days.append({
                'date': day,
                'tasks': PreventiveTask.objects.filter(
                    next_due__year=day.year,
                    next_due__month=day.month,
                    next_due__day=day.day
                )
            })
        
        context.update({
            'days': days,
            'week_start': start_date,
            'week_end': end_date,
            'prev_week': (start_date - timedelta(days=7)).strftime('%Y-%m-%d'),
            'next_week': (start_date + timedelta(days=7)).strftime('%Y-%m-%d'),
        })
        return context

class TemperatureReadingUpdateView(UpdateView):
    model = TemperatureReading
    form_class = TemperatureReadingForm
    template_name = 'preventive/temperature_reading_form.html'
    success_url = reverse_lazy('preventive:temperature_readings')

class TemperatureReadingDeleteView(DeleteView):
    model = TemperatureReading
    template_name = 'preventive/temperature_reading_confirm_delete.html'
    success_url = reverse_lazy('preventive:temperature_readings')

class TemperatureReadingDetailView(DetailView):
    model = TemperatureReading
    template_name = 'preventive/temperature_reading_detail.html'

class PreventiveTaskCreateView(CreateView):
    model = PreventiveTask
    form_class = PreventiveTaskForm
    template_name = 'preventive/task_form.html'
    success_url = reverse_lazy('preventive:calendar')

    def get(self, request, *args, **kwargs):
        print("Méthode GET - Initialisation du formulaire")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print("\n=== DONNÉES POST ===")
        print("Raw POST data:", request.POST)
        
        form = self.get_form()
        if not form.is_valid():
            print("!!! ERREURS DE FORMULAIRE !!!")
            print(form.errors)
            return self.form_invalid(form)
        
        print("Formulaire valide. Données nettoyées:")
        print(form.cleaned_data)
        return self.form_valid(form)

    def form_valid(self, form):
        print("Tentative de sauvegarde...")
        try:
            self.object = form.save(commit=False)
            print("Objet avant sauvegarde finale:", self.object.__dict__)
            self.object.save()
            messages.success(self.request, "Opération enregistrée avec succès!")
            print("Sauvegarde réussie. Redirection...")
            return HttpResponseRedirect(self.get_success_url())
        except Exception as e:
            print("Échec de la sauvegarde:", str(e))
            return self.form_invalid(form)

    def form_invalid(self, form):
        self.object = None
        print("Affichage du formulaire invalide")
        return self.render_to_response(self.get_context_data(form=form))

class PreventiveTaskUpdateView(UpdateView):
    model = PreventiveTask
    #fields = ['equipment', 'task_type', 'description', 'scheduled_date', 'duration_hours', 'technician', 'completed']
    form_class = PreventiveTaskForm
    template_name = 'preventive/task_edit.html'
    success_url = reverse_lazy('preventive:calendar')

class PreventiveTaskDeleteView(DeleteView):
    model = PreventiveTask
    template_name = 'preventive/task_confirm_delete.html'
    success_url = reverse_lazy('preventive:calendar')

class PreventiveCalendarView(ListView):
    model = PreventiveTask
    template_name = 'preventive/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        date_str = self.request.GET.get('date')
        if date_str:
            current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            current_date = timezone.now().date()
        
        start_date = current_date - timedelta(days=current_date.weekday())
        end_date = start_date + timedelta(days=6)
        
        tasks = PreventiveTask.objects.filter(
            next_due__gte=start_date,
            next_due__lte=end_date
        ).select_related('equipment')
        
        days = [start_date + timedelta(days=i) for i in range(7)]
        
        context.update({
            'days': days,
            'tasks': tasks,
            'prev_week': (start_date - timedelta(days=7)).strftime('%Y-%m-%d'),
            'next_week': (start_date + timedelta(days=7)).strftime('%Y-%m-%d'),
            'current_week': start_date.strftime('%Y-%m-%d'),
        })
        return context