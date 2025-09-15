from django.urls import path
from . import views

app_name = 'etudiants'

urlpatterns = [
    path('', views.list_etudiants, name='liste_etudiants'),
    path('ajouter/', views.ajouter_etudiant, name='ajouter_etudiant'),
    #path('<int:etudiant_id>/', views.detail_etudiant, name='detail_etudiant'),
    #path('<int:etudiant_id>/ajouter-note/', views.ajouter_note, name='ajouter_note'),
    #path('<int:etudiant_id>/supprimer/', views.supprimer_etudiant, name='supprimer_etudiant'),
]