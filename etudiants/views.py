
from django.shortcuts import render, redirect
from .models import User, notes
from django .db import connection
from django.contrib import messages

def list_etudiants(request):
    with connection.cursor() as cursor :
        cursor.execute("SELECT id, nom, prenom, email, contact FROM etudiants_user")
        rows = cursor.fetchall()
        
    etudiants = []
    for r in rows:
        etudiants.append({
            'id': r[0],
            'nom': r[1],
            'prenom': r[2],
            'email': r[3],
            'contact': r[4],
            })

    return render(request, 'etudiants/home.html', {'etudiants':etudiants})

def ajouter_etudiant(request):
    message = None
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
    
        if nom and prenom and email and contact :
            with connection.cursor() as cursor:
                sql = "INSERT INTO etudiants_user(nom, prenom, email, contact, is_valid) VALUES(%s, %s, %s, %s, 1)"
                cursor.execute(sql, [nom, prenom, email, contact])
                message = "Étudiants ajouté avec succès"
            return redirect('etudiants:liste_etudiants')
        message = "Veuillez vérifier que vous avez rempli tous les champs d'ajout"
    return render(request, 'etudiants/ajouter_etudiant.html', {'message': message})

from django.shortcuts import render
from django.db import connection
from django.contrib import messages

def detail_etudiants(request, etudiant_id):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, nom, prenom, email, contact 
        FROM etudiants_user 
        WHERE id = %s
    """, [etudiant_id])
    etudiant = cursor.fetchone()

    if not etudiant:
        messages.error(request, "Étudiant introuvable.")
        return render(request, 'etudiants/detail_etudiants.html', {'etudiant': None})
    matieres_fixes = ['Django', 'Python', 'CSS', 'Bootstrap', 'SQL']

    cursor.execute("""
        SELECT matiere, interrogation, devoir, devoirs, coefficent 
        FROM etudiants_notes 
        WHERE id = %s
    """, [etudiant_id])
    notes_data = cursor.fetchall()
    notes_dict = {row[0]: row for row in notes_data}

    notes_par_matiere = []
    total_moyenne = 0
    total_ponderee = 0
    total_coeff = 0

    for matiere in matieres_fixes:
        if matiere in notes_dict:
            interrogation, devoir, devoirs, coeff = notes_dict[matiere][1], notes_dict[matiere][2], notes_dict[matiere][3], notes_dict[matiere][4]
            interrogation = interrogation or 0
            devoir = devoir or 0
            devoirs = devoirs or 0
            coeff = coeff or 1
            moyenne = (interrogation + devoir + devoirs) / 3
            moyenne_ponderee = moyenne * coeff

            total_moyenne += moyenne
            total_ponderee += moyenne_ponderee
            total_coeff += coeff

            notes_par_matiere.append({
                'matiere': matiere,
                'interrogation': interrogation,
                'devoir': devoir,
                'devoirs': devoirs,
                'coeff': coeff,
                'moyenne': round(moyenne, 2)
            })
        else:
            notes_par_matiere.append({
                'matiere': matiere,
                'interrogation': 0,
                'devoir': 0,
                'devoirs': 0,
                'coeff': 1,
                'moyenne': 0
            })

    moyenne_generale = round(total_moyenne / len([n for n in notes_par_matiere if n['moyenne'] is not None]), 2) if total_moyenne else 0
    moyenne_ponderee = round(total_ponderee / total_coeff, 2) if total_coeff else 0

    return render(request, 'etudiants/detail_etudiants.html', {
        'etudiant': etudiant,
        'notes_par_matiere': notes_par_matiere,
        'moyenne_generale': moyenne_generale,
        'moyenne_ponderee': moyenne_ponderee
    })

def voir_note_and_avg(request, etudiant_id) :
    return ()
def ajouter_notes(request, etudiant_id):
    return()
def supprimer_etudiants(request, etudiant_id):
    if request.method == 'POST' :
        try:
            with connection.cursor() as cursor :
                cursor.execute("DELETE FROM etudiants_user WHERE id = %s", [etudiant_id])
                messages.success(request, "Étudiants supprimé avec succès")
                return redirect('etudiants:liste_etudiants')
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression: {str(e)}")
            return redirect('etudiants:liste_etudiants')
    else :
        return render(request, 'etudiants/home.html', {'etudiant_id':etudiant_id})

