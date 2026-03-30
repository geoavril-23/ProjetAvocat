from .models import SiteConfiguration, UserProfile

def site_config(request):
    config = SiteConfiguration.objects.first()
    theme = 'LIGHT'
    if request.user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        theme = profile.theme_pref
        
    return {
        'site_config': config,
        'user_theme': theme
    }
