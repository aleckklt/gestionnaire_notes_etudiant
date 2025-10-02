from django.urls import path
from . import views

app_name = 'etudiants'

urlpatterns = [
    path('', views.list_etudiants, name='liste_etudiants'),
    path('ajouter/', views.ajouter_etudiant, name='ajouter_etudiant'),
    path('<int:etudiant_id>/', views.detail_etudiants, name='detail_etudiant'),
    path('api/etudiants/', views.api_list_etudiants, name='api_list_etudiants'),
    path('api/etudiants/create/', views.api_create_etudiant, name='api_create_etudiant'),
    path('api/etudiants/<int:etudiant_id>/desactiver/', views.api_desactiver_etudiant, name='api_desactiver_etudiant'),
    path('api/etudiants/<int:etudiant_id>/activer/', views.api_activer_etudiant, name='api_activer_etudiant'),
    path('api/etudiants/<int:etudiant_id>/detail/', views.api_detail_etudiant, name='api_detail_etudiant'),
    path('api/etudiants/<int:etudiant_id>/modifier_notes/', views.api_modifier_notes_etudiant, name='api_modifier'),   
]