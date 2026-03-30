from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import DemandeService, Visite, SiteConfiguration, UserProfile

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def track_visite(request):
    """Enregistre une visite unique par IP par jour"""
    ip = get_client_ip(request)
    today = timezone.now().date()
    if not Visite.objects.filter(ip_adresse=ip, date_visite__date=today).exists():
        Visite.objects.create(ip_adresse=ip)

def index(request):
    track_visite(request)
    return render(request, 'index.html')

def domaine_pratique(request):
    track_visite(request)
    return render(request, 'domaine_pratique.html')

def contact(request):
    track_visite(request)
    if request.method == "POST":
        return soumettre_demande(request)
    return render(request, 'contact.html')

def cas_etudes(request):
    track_visite(request)
    return render(request, 'cas_etudes.html')

def about(request):
    track_visite(request)
    return render(request, 'about.html')

def soumettre_demande(request):
    if request.method == "POST":
        nom = request.POST.get('nom', 'Anonyme')
        prenom = request.POST.get('prenom', '')
        email = request.POST.get('email', '')
        telephone = request.POST.get('telephone', '')
        description = request.POST.get('description', '')
        domaine = request.POST.get('domaine', 'FONCIER')

        DemandeService.objects.create(
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone,
            description=description,
            domaine=domaine
        )
        messages.success(request, "Votre demande a bien été envoyée. Nous vous contacterons bientôt.")
        # Redirection vers l'accueil ou le point d'origine
        return redirect('index')        
    return redirect('index')

# ================================
# DASHBOARD ADMINISTRATIF
# ================================

def admin_login(request):
    # Si déjà connecté, on affiche quand même la page avec un message pour permettre la déconnexion
    if request.user.is_authenticated:
        messages.info(request, f"Vous êtes actuellement connecté en tant que {request.user.username}. Déconnectez-vous pour changer de compte.")
        # On ne redirige pas automatiquement ici pour laisser l'utilisateur voir le formulaire s'il veut changer
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Identifiants invalides.")
            
    return render(request, 'admin/login.html')

def admin_logout(request):
    logout(request)
    return redirect('index')

@login_required
def admin_dashboard(request):
    # Filtres Temporels
    filter_type = request.GET.get('filter', '')
    now = timezone.now()
    
    if filter_type == 'jour':
        start_date = now - timedelta(days=1)
    elif filter_type == 'semaine':
        start_date = now - timedelta(days=7)
    elif filter_type == 'mois':
        start_date = now - timedelta(days=30)
    else:
        start_date = None

    # Querysets de base
    visites = Visite.objects.all()
    demandes = DemandeService.objects.all()

    if start_date:
        visites = visites.filter(date_visite__gte=start_date)
        demandes = demandes.filter(date_creation__gte=start_date)

    # Statistiques Globales (Disponibles pour tous les types d'admins)
    context = {
        'nb_visiteurs': visites.count(),
        'total_demandes': demandes.count(),
        'nb_en_attente': demandes.filter(statut__in=['ATTENTE', 'EN_COURS']).count(),
        'nb_termines': demandes.filter(statut='TERMINE').count(),
        'current_filter': filter_type,
    }

    # Données détaillées (Uniquement pour le profil AVOCAT)
    if request.user.profile.role == 'AVOCAT':
        context.update({
            'demandes_attente': demandes.filter(statut='ATTENTE').order_by('-date_creation'),
            'demandes_en_cours': demandes.filter(statut='EN_COURS').order_by('-date_creation'),
            'demandes_terminees': demandes.filter(statut='TERMINE').order_by('-date_cloture'),
        })

    return render(request, 'admin/index.html', context)


@login_required
def update_statut_demande(request, id):
    if request.method == "POST":
        nouveau_statut = request.POST.get('nouveau_statut')
        demande = get_object_or_404(DemandeService, id=id)
        
        if nouveau_statut in dict(DemandeService.STATUTS):
            demande.statut = nouveau_statut
            if nouveau_statut == 'TERMINE':
                demande.date_cloture = timezone.now()
            demande.save()
            messages.success(request, f"Le statut de {demande.nom} a été mis à jour.")
    
    return redirect('admin_dashboard')


@login_required
def admin_settings(request):
    # Récupérer ou créer la config globale et le profil utilisateur
    config, created_c = SiteConfiguration.objects.get_or_create(id=1)
    profile, created_p = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        # 1. Mise à jour du thème personnel (Accessible à TOUS)
        theme_perso = request.POST.get('theme_perso')
        if theme_perso in ['LIGHT', 'DARK']:
            profile.theme_pref = theme_perso
            profile.save()
            messages.success(request, f"Votre thème personnel est maintenant : {profile.get_theme_pref_display()}.")

        # 2. Mise à jour des paramètres du cabinet (ADMIN uniquement)
        if request.user.profile.role == 'ADMIN':
            nom_cabinet = request.POST.get('nom_cabinet')
            if nom_cabinet:
                config.nom_cabinet = nom_cabinet
                config.save()
                messages.success(request, "Les paramètres du cabinet ont été mis à jour.")
        
        return redirect('admin_settings')

    context = {
        'config': config,
        'profile': profile,
    }
    return render(request, 'admin/settings.html', context)

from django.contrib.auth.models import User

# --- GESTION DES UTILISATEURS (ADMIN UNIQUEMENT) ---

@login_required
def admin_users_list(request):
    if request.user.profile.role != 'ADMIN':
        messages.error(request, "Accès réservé à l'administrateur.")
        return redirect('admin_dashboard')
    
    users = User.objects.all().order_by('-date_joined')
    
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            profile = user.profile
            profile.role = role
            profile.save()
            messages.success(request, f"L'utilisateur {username} a été créé avec succès.")
            return redirect('admin_users_list')

    return render(request, 'admin/admin_users.html', {'users': users})

@login_required
def admin_delete_user(request, user_id):
    if request.user.profile.role != 'ADMIN':
        return redirect('admin_dashboard')
    
    user_to_delete = get_object_or_404(User, id=user_id)
    if user_to_delete.is_superuser:
        messages.error(request, "Impossible de supprimer un super-utilisateur.")
    else:
        user_to_delete.delete()
        messages.success(request, "Utilisateur supprimé.")
    return redirect('admin_users_list')


# --- CRUD DOSSIERS (ADMIN UNIQUEMENT) ---

@login_required
def admin_edit_demande(request, id):
    if request.user.profile.role != 'ADMIN':
        return redirect('admin_dashboard')
    
    demande = get_object_or_404(DemandeService, id=id)
    
    if request.method == "POST":
        demande.nom = request.POST.get('nom')
        demande.prenom = request.POST.get('prenom')
        demande.email = request.POST.get('email')
        demande.telephone = request.POST.get('telephone')
        demande.domaine = request.POST.get('domaine')
        demande.statut = request.POST.get('statut')
        demande.description = request.POST.get('description')
        demande.save()
        messages.success(request, "Le dossier a été mis à jour.")
        return redirect('admin_consultations')
    
    return render(request, 'admin/edit_demande.html', {'demande': demande})

@login_required
def admin_delete_demande(request, id):
    if request.user.profile.role != 'ADMIN':
        return redirect('admin_dashboard')
    
    demande = get_object_or_404(DemandeService, id=id)
    demande.delete()
    messages.success(request, "Dossier supprimé définitivement.")
    return redirect('admin_consultations')

@login_required
def admin_consultations(request):
    demandes = DemandeService.objects.all().order_by('-date_creation')
    return render(request, 'admin/consultations.html', {'demandes': demandes})
