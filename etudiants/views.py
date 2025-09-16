
from django.shortcuts import render, redirect
from .models import User, notes
from django .db import connection

def list_etudiants(request):
    with connection.cursor() as cursor :
        cursor.execute("SELECT id, nom, prenom, email, contact, classes FROM etudiants_user")
        rows = cursor.fetchall()
        
    etudiants = []
    for r in rows:
        etudiants.append({
            'id': r[0],
            'nom': r[1],
            'prenom': r[2],
            'email': r[3],
            'contact': r[4],
            'classes': r[5],
            })

    return render(request, 'etudiants/home.html', {'etudiants':etudiants})

def ajouter_etudiant(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        classes = request.POST.get('classe')
    
        if nom and prenom and email and contact and classes:
            with connection.cursor() as cursor:
                sql = "INSERT INTO etudiants_user(nom, prenom, email, contact, classes, is_valid) VALUES(%s, %s, %s, %s, %s, 1)"
                cursor.execute(sql, [nom, prenom, email, contact, classes])

            return redirect('etudiants:list_etudiants')
        else:
            message = "Veuillez vérifier que vous avez rempli tous les champs d'ajout"
            return render(request, 'etudiants/ajouter_etudiant.html', {'message': message})
        
    return render(request, 'etudiants/ajouter_etudiant.html')

def detail_etudiants(request, etudiant_id) :
    return()
def ajouter_notes(request, etudiant_id):
    return()
def supprimer_etudiants(request, etudiant_id):
    return()
