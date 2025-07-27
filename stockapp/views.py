from django.shortcuts import render, get_object_or_404, redirect
from .models import Produit, Categorie, Commande, MouvementStock
from .forms import ProduitForm, CommandeForm  
from django.views.decorators.http import require_POST
from django.db.models import Count, Sum, Q, F
from .forms import MouvementStockForm
from django.contrib import messages
from .utils import render_to_pdf
from .models import Commande
from django.utils.timezone import now
from django.http import JsonResponse

def produits_par_categorie(request, categorie_id):
    categorie = get_object_or_404(Categorie, pk=categorie_id)
    produits = Produit.objects.filter(categorie_id=categorie_id).order_by('-date_maj')
    form = ProduitForm()
    mouvement_form = MouvementStockForm()

    if request.method == 'POST':
        if 'ajouter_produit' in request.POST:
            product_id = request.POST.get('product_id')
            form = ProduitForm(request.POST, request.FILES)

            if form.is_valid():
                if product_id:  # Modification
                    produit = get_object_or_404(Produit, pk=product_id)
                    for field, value in form.cleaned_data.items():
                        setattr(produit, field, value)
                    produit.categorie = categorie
                    produit.save()
                else:  # Ajout
                    nouveau_produit = form.save(commit=False)
                    nouveau_produit.categorie = categorie
                    nouveau_produit.save()
                return redirect('stockapp:produits_categorie', categorie_id=categorie.id)

        elif 'enregistrer_mouvement' in request.POST:
            mouvement_form = MouvementStockForm(request.POST)
            if mouvement_form.is_valid():
                mouvement = mouvement_form.save(commit=False)
                mouvement.effectue_par = request.user.username
                mouvement.save()

                produit = mouvement.produit
                if mouvement.type == 'entree':
                    produit.quantite += mouvement.quantite
                else:
                    if mouvement.quantite > produit.quantite:
                        mouvement.delete()
                        messages.error(request, "Stock insuffisant pour cette sortie.")
                        return redirect('stockapp:produits_categorie', categorie_id=categorie.id)
                    produit.quantite -= mouvement.quantite
                produit.save()
                return redirect('stockapp:produits_categorie', categorie_id=categorie.id)

    return render(request, 'stockapp/produits_categorie.html', {
        'categorie': categorie,
        'produits': produits,
        'form': form,
        'mouvement_form': mouvement_form
    })


def produits_alerte(request):
    produits = Produit.objects.filter(quantite__lte=F('stock_alerte')).order_by('quantite')
    return render(request, 'stockapp/produits_alerte.html', {'produits': produits})

def index(request):
    # Stats globales
    total_produits = Produit.objects.count()
    produits_alerte = Produit.objects.filter(quantite__lte=F('stock_alerte')).count()
    
    # Stats par catégorie
    categories = Categorie.objects.annotate(
        nb_produits=Count('produit'),
        nb_alertes=Count('produit', filter=Q(produit__quantite__lte=F('produit__stock_alerte')))
    )
    
    # Derniers produits et commandes
    derniers_produits = Produit.objects.order_by('-date_creation')[:5]
    dernieres_commandes = Commande.objects.order_by('-date')[:5]
    
    return render(request, 'stockapp/index.html', {
        'total_produits': total_produits,
        'produits_alerte': produits_alerte,
        'categories': categories,
        'derniers_produits': derniers_produits,
        'dernieres_commandes': dernieres_commandes
    })

def categories(request):
    # Si aucune catégorie n'existe, créons les catégories par défaut
    if Categorie.objects.count() == 0:
        Categorie.creer_categories_par_defaut()
    
    categories = Categorie.objects.all()
    return render(request, 'stockapp/categories.html', {'categories': categories})

@require_POST
def modifier_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    form = ProduitForm(request.POST, request.FILES, instance=produit)  # Notez request.FILES
    if form.is_valid():
        form.save()
    return redirect('stockapp:produits_categorie', categorie_id=produit.categorie.id)

def supprimer_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    categorie_id = produit.categorie.id
    produit.delete()
    return redirect('stockapp:produits_categorie', categorie_id=categorie_id)

def creer_commande(request, categorie_id):
    categorie = get_object_or_404(Categorie, pk=categorie_id)
    
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            commande = form.save(commit=False)
            commande.categorie = categorie
            commande.status = 'attente'
            commande.save()
            return redirect('stockapp:produits_categorie', categorie_id=categorie.id)
    else:
        form = CommandeForm()

    return render(request, 'stockapp/nouvelle_commande.html', {
        'categorie': categorie,
        'form': form
    })

def historique_commandes(request, categorie_id):
    categorie = get_object_or_404(Categorie, pk=categorie_id)
    commandes = Commande.objects.filter(categorie=categorie).order_by('-date')
    
    return render(request, 'stockapp/historique_commandes.html', {
        'categorie': categorie,
        'commandes': commandes,
    })

def historique_commandes_all(request):
    categories = Categorie.objects.annotate(
        nb_commandes=Count('commande')
    ).filter(nb_commandes__gt=0)
    
    return render(request, 'stockapp/historique_commandes_all.html', {
        'categories': categories,
        
    })

def historique_commandes_pdf(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    commandes = Commande.objects.filter(categorie=categorie)
    return render_to_pdf('stockapp/pdf/historique_commandes_pdf.html', {
        'categorie': categorie,
        'commandes': commandes,
        'now': now()
    })


@require_POST
def valider_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    commande.status = 'validee'
    commande.save()
    return redirect('stockapp:historique_commandes', categorie_id=commande.categorie.id)

def commande_pdf(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    return render_to_pdf('stockapp/pdf/commande.html', {'commande': commande})

@require_POST
def rejeter_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    commande.status = 'rejetee'
    commande.save()
    return redirect('stockapp:historique_commandes', categorie_id=commande.categorie.id)


def historique_mouvements(request, categorie_id):
    categorie = get_object_or_404(Categorie, pk=categorie_id)
    mouvements = MouvementStock.objects.filter(produit__categorie=categorie).order_by('-date')
    return render(request, 'stockapp/historique_mouvements.html', {
        'categorie': categorie,
        'mouvements': mouvements
    })

def mouvement_pdf(request, mouvement_id):
    mouvement = get_object_or_404(MouvementStock, id=mouvement_id)
    return render_to_pdf('stockapp/pdf/mouvement.html', {'mouvement': mouvement})

def historique_mouvements_pdf(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    mouvements = MouvementStock.objects.filter(produit__categorie=categorie).order_by('-date')
    return render_to_pdf('stockapp/pdf/historique_mouvements.html', {
    'categorie': categorie,
    'mouvements': mouvements,
    'now': now()
    })


def produit_stock(request, pk):
    """
    API rapide qui renvoie la quantité en stock du produit pk.
    """
    prod = get_object_or_404(Produit, pk=pk)
    return JsonResponse({'quantite': prod.quantite})


