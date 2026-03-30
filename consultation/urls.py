from django.urls import path
from . import views

urlpatterns=[
    path('', views.index , name='index'),
    path('domaine_pratique/', views.domaine_pratique , name='domaine_pratique'),
    path('contact/', views.contact , name='contact'),
    path('cas_etudes/', views.cas_etudes , name='cas_etudes'),
    path('about/', views.about , name='about'),
    path('soumettre_demande/', views.soumettre_demande , name='soumettre_demande'),
    
    # Authentification
    path('dashboard/login/', views.admin_login, name='admin_login'),
    path('dashboard/logout/', views.admin_logout, name='admin_logout'),
    
    # Dashboad
    path('dashboard/', views.admin_dashboard , name='admin_dashboard'),
    # Administration & Contrôle (CRUD)
    path('dashboard/users/', views.admin_users_list , name='admin_users_list'),
    path('dashboard/users/delete/<int:user_id>/', views.admin_delete_user , name='admin_delete_user'),
    path('dashboard/demande/edit/<int:id>/', views.admin_edit_demande , name='admin_edit_demande'),
    path('dashboard/demande/delete/<int:id>/', views.admin_delete_demande , name='admin_delete_demande'),
    path('dashboard/update_statut/<int:id>/', views.update_statut_demande , name='update_statut_demande'),
    path('dashboard/consultations/', views.admin_consultations , name='admin_consultations'),
    path('dashboard/settings/', views.admin_settings , name='admin_settings'),
]