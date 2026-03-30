from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Visite, DemandeService, UserProfile, SiteConfiguration

# Permet d'éditer le profil directement dans la fiche Utilisateur de Django
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil Utilisateur'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Ré-enregistrement du modèle User avec l'Inline
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Enregistrement des autres modèles
@admin.register(DemandeService)
class DemandeServiceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'domaine', 'statut', 'date_creation')
    list_filter = ('statut', 'domaine')
    search_fields = ('nom', 'prenom', 'email')

@admin.register(Visite)
class VisiteAdmin(admin.ModelAdmin):
    list_display = ('date_visite', 'ip_adresse')

admin.site.register(SiteConfiguration)
