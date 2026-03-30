from django.contrib.auth.models import User
from consultation.models import UserProfile

for u in User.objects.all():
    p, c = UserProfile.objects.get_or_create(user=u)
    if u.is_superuser:
        p.role = 'ADMIN'
    else:
        p.role = 'AVOCAT'
    p.save()
    print(f'User {u.username} role: {p.role}')
