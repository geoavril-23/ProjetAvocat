from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# 1. Modèle pour le filtrage des statistiques du Dashboard
class Visite(models.Model):
    """Enregistre chaque accès pour les stats jours/semaine/mois"""
    date_visite = models.DateTimeField(default=timezone.now)
    ip_adresse = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"Visite du {self.date_visite}"

# 2. Modèle principal pour les Demandes et le Suivi des Dossiers
class DemandeService(models.Model):
    DOMAINES = [
        ('FONCIER', 'Foncier et Immobilier'),
        ('FAMILLE', 'Droit de la Famille'),
        ('TRAVAIL', 'Droit du Travail'),
        ('AFFAIRES', 'Droit des Affaires'),
    ]

    STATUTS = [
        ('ATTENTE', 'En attente'),
        ('EN_COURS', 'Service en cours de traitement'),
        ('TERMINE', 'Cas terminé / Archivé'),
    ]

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    domaine = models.CharField(max_length=20, choices=DOMAINES, default='FONCIER')
    description = models.TextField(verbose_name="Description du service")
    statut = models.CharField(max_length=20, choices=STATUTS, default='ATTENTE')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_cloture = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.get_statut_display()}"

# 3. Profil Utilisateur (Configuration individuelle)
class UserProfile(models.Model):
    ROLES = [
        ('ADMIN', 'Administrateur Technique'),
        ('AVOCAT', 'Avocat'),
    ]
    THEMES = [
        ('LIGHT', 'Mode Clair'),
        ('DARK', 'Mode Sombre'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLES, default='AVOCAT')
    theme_pref = models.CharField(max_length=10, choices=THEMES, default='LIGHT')

    def __str__(self):
        return f"Profil de {self.user.username} ({self.get_role_display()})"

# Automatisme : Créer un profil dès qu'un utilisateur est créé
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# 4. Modèle pour les Paramètres Globaux (Sans le thème)
class SiteConfiguration(models.Model):
    nom_cabinet = models.CharField(max_length=100, default="FOYAK TOGO")

    def __str__(self):
        return "Configuration du site"