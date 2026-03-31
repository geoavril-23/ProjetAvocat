import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projetAvocat.settings')
django.setup()

from django.contrib.auth.models import User
from consultation.models import UserProfile

def create_accounts():
    # 1. Création de l'ADMIN
    if not User.objects.filter(username='georges.awesso@ipnetinstitute.com').exists():
        u = User.objects.create_superuser('georges.awesso@ipnetinstitute.com', '', 'Essodon7055@')
        u.profile.role = 'ADMIN'
        u.profile.save()
        print(f"Compte ADMIN '{u.username}' créé avec succès !")
    else:
        print("Le compte ADMIN existe déjà.")

    # 2. Création de l'AVOCAT
    if not User.objects.filter(username='maitre@gmail.com').exists():
        u = User.objects.create_superuser('maitre@gmail.com', '', '3432')
        # Par défaut le signal met le rôle AVOCAT, on s'en assure quand même
        u.profile.role = 'AVOCAT'
        u.profile.save()
        print(f"Compte AVOCAT '{u.username}' créé avec succès !")
    else:
        print("Le compte AVOCAT existe déjà.")

if __name__ == "__main__":
    create_accounts()
