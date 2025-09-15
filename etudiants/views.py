
from django.shortcuts import render, redirect
from .models import User, notes
from django .db import connection
from .forms import etudiantsForm

def list_etudiants(request):
    liste = User.objects.raw('SELECT * FROM User WHERE is_valid = True')
    return render(request, 'etudiants/home.html', {'liste' : liste})

def ajouter_etudiant(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        classes = request.POST.get('classe')
    
        if nom and prenom and email and contact and classes:
            with connection.cursor() as cursor :
                sql = "INSERT INTO etudiants_user(nom, prenom, email, contact, classes) VALUES(%s, %s, %s, %s, %s)"
                cursor.execute(sql, [nom, prenom, email, contact, classes])
                message = "L'étudiant a été ajouté avec succès"
        else:
            message = "Veuillez vérifier que vous avez rempli tous les champs d'ajout"
    else:
        message = "Etudiant ajouté"

    return render(request, 'etudiants/ajouter_etudiant.html', {'message':message})