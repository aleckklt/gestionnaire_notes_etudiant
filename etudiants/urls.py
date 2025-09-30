from django.urls import path
from . import views

app_name = 'etudiants'

urlpatterns = [
    path('', views.list_etudiants, name='liste_etudiants'),
    path('ajouter/', views.ajouter_etudiant, name='ajouter_etudiant'),
    path('<int:etudiant_id>/', views.detail_etudiants, name='detail_etudiant'),
    path('api/etudiants/', views.etudiant_list_api, name='api_list_etudiants'),
    path('api/etudiants/create/', views.ajouter_etudiant_api, name='api_create_etudiant'),
    path('api/etudiants/<int:etudiant_id>/', views.detail_etudiants_api, name='api_detail_etudiant'),
]