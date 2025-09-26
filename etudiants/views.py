
from django.shortcuts import render, redirect
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
    
        if nom and prenom and email and contact:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM etudiants_user WHERE email = %s", [email])
                count = cursor.fetchone()[0]
                if count > 0:
                    message = "Un étudiant avec cet email existe déjà."
                else:
                    sql = "INSERT INTO etudiants_user(nom, prenom, email, contact, is_valid) VALUES(%s, %s, %s, %s, 1)"
                    cursor.execute(sql, [nom, prenom, email, contact])
                    messages.success(request, "Étudiant ajouté avec succès.")
                    return redirect('etudiants:liste_etudiants')
        else:
            message = "Veuillez remplir tous les champs."

    return render(request, 'etudiants/ajouter_etudiant.html', {'message': message})

def detail_etudiants(request, etudiant_id):
    
    with connection.cursor() as cursor:
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
    notes_par_matiere = []
    moyenne_generale = 0
    moyenne_ponderee = 0

    if request.method == 'POST':
        action = request.POST.get('action')
        nb_matieres = int(request.POST.get('nb_matieres', 0))

        total_moyenne = 0
        total_ponderee = 0
        total_coeff = 0

        for i in range(1, nb_matieres + 1):
            matiere = request.POST.get(f'matiere_{i}')
            interrogation1 = float(request.POST.get(f'interrogation1_{i}', 0) or 0)
            devoir = float(request.POST.get(f'devoir_{i}', 0) or 0)
            interrogation2 = float(request.POST.get(f'interrogation2_{i}', 0) or 0)
            coefficients = float(request.POST.get(f'coefficients_{i}', 1) or 1)

            moyenne = round((interrogation1 + devoir + interrogation2) / 3, 2)
            moyenne_ponderee_calc = moyenne * coefficients

            total_moyenne += moyenne
            total_ponderee += moyenne_ponderee_calc
            total_coeff += coefficients

            notes_par_matiere.append({
                'matiere': matiere,
                'interrogation1': interrogation1,
                'devoir': devoir,
                'interrogation2': interrogation2,
                'coefficients': coefficients,
                'moyenne': moyenne
            })

            if action == 'enregistrer':
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id FROM etudiants_notes
                        WHERE note_id = %s
                    """, [etudiant_id])
                    exists = cursor.fetchall()
                    if exists:
                        cursor.execute("""
                            UPDATE etudiants_notes
                            SET interrogation1 = %s, interrogation2 = %s, devoir = %s, coefficients = %s
                            WHERE note_id = %s AND matiere = %s
                        """, [interrogation1, interrogation2, devoir,coefficients, etudiant_id, matiere])
                    else:
                        cursor.execute("""
                            INSERT INTO etudiants_notes (note_id, matiere, interrogation1, interrogation2, devoir, coefficients)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """,[interrogation1, interrogation2, devoir,coefficients, etudiant_id, matiere])

        moyenne_generale = round(total_moyenne / nb_matieres, 2) if nb_matieres else 0
        moyenne_ponderee = round(total_ponderee / total_coeff, 2) if total_coeff else 0

        if action == 'enregistrer':
            messages.success(request, "Les notes ont été enregistrées avec succès.")
        elif action == 'calculer':
            messages.info(request, "Les moyennes ont été recalculées (non enregistrées).")

    else:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT matiere, interrogation1, interrogation2, devoir, coefficients
                FROM etudiants_notes 
                WHERE note_id = %s
            """, [etudiant_id])
            notes_data = cursor.fetchall()
            notes_dict = {row[0]: row for row in notes_data}

        total_moyenne = 0
        total_ponderee = 0
        total_coeff = 0

        for matiere in matieres_fixes:
            if matiere in notes_dict:
                interrogation1, interrogation2, devoir, coefficients = notes_dict[matiere][1], notes_dict[matiere][2], notes_dict[matiere][3], notes_dict[matiere][4]
                interrogation1 = interrogation1 or 0
                devoir = devoir or 0
                interrogation2 = interrogation2 or 0
                coefficients = coefficients or 1
                moyenne = round((interrogation1 + devoir + interrogation2) / 3, 2)
                moyenne_ponderee_calc = moyenne * coefficients

                total_moyenne += moyenne
                total_ponderee += moyenne_ponderee_calc
                total_coeff += coefficients

                notes_par_matiere.append({
                    'matiere': matiere,
                    'interrogation1': interrogation1,
                    'devoir': devoir,
                    'interrogation2': interrogation2,
                    'coefficients': coefficients,
                    'moyenne': moyenne
                })
            else:
                notes_par_matiere.append({
                    'matiere': matiere,
                    'interrogation1': 0,
                    'devoir': 0,
                    'interrogation2': 0,
                    'coefficients': 1,
                    'moyenne': 0
                })

        moyenne_generale = round(total_moyenne / len(notes_par_matiere), 2) if notes_par_matiere else 0
        moyenne_ponderee = round(total_ponderee / total_coeff, 2) if total_coeff else 0

    return render(request, 'etudiants/detail_etudiants.html', {
        'etudiant': etudiant,
        'notes_par_matiere': notes_par_matiere,
        'moyenne_generale': moyenne_generale,
        'moyenne_ponderee': moyenne_ponderee
    })

