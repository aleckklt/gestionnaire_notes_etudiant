from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer

def list_etudiants(request):
    if request.method == 'POST':
        etudiant_id = request.POST.get('etudiant_id')
        action = request.POST.get('action')
        
        if etudiant_id and action:
            with connection.cursor() as cursor:
                if action == 'desactiver':
                    cursor.execute("UPDATE etudiants_user SET is_valid = 0 WHERE id = %s", [etudiant_id])
                    messages.success(request, "Étudiant désactivé avec succès.")
                elif action == 'activer':
                    cursor.execute("UPDATE etudiants_user SET is_valid = 1 WHERE id = %s", [etudiant_id])
                    messages.success(request, "Étudiant activé avec succès.")
            
            return redirect('etudiants:liste_etudiants')

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nom, prenom, email, contact, is_valid FROM etudiants_user")
        rows = cursor.fetchall()
        
    etudiants = []
    for r in rows:
        etudiants.append({
            'id': r[0],
            'nom': r[1],
            'prenom': r[2],
            'email': r[3],
            'contact': r[4],
            'is_valid': r[5]
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
                    sql = "INSERT INTO etudiants_user(nom, prenom, email, contact, is_valid) VALUES(%s, %s, %s, %s, 0)"
                    cursor.execute(sql, [nom, prenom, email, contact])
                    messages.success(request, "Étudiant ajouté avec succès.")
                    return redirect('etudiants:liste_etudiants')
        else:
            message = "Veuillez remplir tous les champs."

    return render(request, 'etudiants/ajouter_etudiant.html', {'message': message})

def detail_etudiants(request, etudiant_id):
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, nom, prenom, email, contact, is_valid
            FROM etudiants_user 
            WHERE id = %s
        """, [etudiant_id])
        etudiant = cursor.fetchone()

    if not etudiant:
        messages.error(request, "Étudiant introuvable.")
        return render(request, 'etudiants/detail_etudiants.html', {'etudiant': None})

    matieres_fixes = ['Python', 'Django', 'CSS', 'Bootstrap', 'SQL']
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
                        WHERE note_id = %s AND matiere = %s
                    """, [etudiant_id, matiere])
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
                        """,[etudiant_id, matiere, interrogation1, interrogation2, devoir, coefficients])

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

@api_view(['GET'])
def api_list_etudiants(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nom, prenom, email, contact, is_valid FROM etudiants_user")
        rows = cursor.fetchall()

    etudiants = []
    for row in rows:
        etudiants.append({
            'id': row[0], 
            'nom': row[1], 
            'prenom': row[2], 
            'email': row[3], 
            'contact': row[4], 
            'is_valid': row[5]
        })

    serializer = UserSerializer(etudiants, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def api_create_etudiant(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        nom = serializer.validated_data['nom']
        prenom = serializer.validated_data['prenom']
        email = serializer.validated_data['email']
        contact = serializer.validated_data['contact']
        is_valid = serializer.validated_data.get('is_valid', False)

        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM etudiants_user WHERE email = %s", [email])
            count = cursor.fetchone()[0]
            if count > 0:
                return Response(
                    {'error': 'Un étudiant avec cet email existe déjà. An etudiant with this email already exists.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cursor.execute(
                "INSERT INTO etudiants_user (nom, prenom, email, contact, is_valid) VALUES (%s, %s, %s, %s, %s)",
                [nom, prenom, email, contact, is_valid]
            )
    
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def api_desactiver_etudiant(request, etudiant_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nom FROM etudiants_user WHERE id = %s", [etudiant_id])
        etudiant = cursor.fetchone()
        
        if not etudiant:
            return Response({'error': 'Étudiant non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        
        cursor.execute("UPDATE etudiants_user SET is_valid = 0 WHERE id = %s", [etudiant_id])
    
    return Response({
        'message': f'Étudiant {etudiant[1]} désactivé avec succès',
        'etudiant_id': etudiant_id
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def api_activer_etudiant(request, etudiant_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nom FROM etudiants_user WHERE id = %s", [etudiant_id])
        etudiant = cursor.fetchone()
        
        if not etudiant:
            return Response({'error': 'Étudiant non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        
        cursor.execute("UPDATE etudiants_user SET is_valid = 1 WHERE id = %s", [etudiant_id])
    
    return Response({
        'message': f'Étudiant {etudiant[1]} activé avec succès',
        'etudiant_id': etudiant_id
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def api_detail_etudiant(request, etudiant_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, nom, prenom, email, contact, is_valid
            FROM etudiants_user 
            WHERE id = %s
        """, [etudiant_id])
        etudiant = cursor.fetchone()

    if not etudiant:
        return Response({'error': 'Étudiant non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    etudiant_data = {
        'id': etudiant[0],
        'nom': etudiant[1],
        'prenom': etudiant[2],
        'email': etudiant[3],
        'contact': etudiant[4],
        'is_valid': etudiant[5]
    }

    matieres_fixes = ['Python', 'Django', 'CSS', 'Bootstrap', 'SQL']
    notes_par_matiere = []
    moyenne_generale = 0
    moyenne_ponderee = 0

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, note_id, matiere, interrogation1, interrogation2, devoir, coefficients
            FROM etudiants_notes 
            WHERE note_id = %s
        """, [etudiant_id])
        notes_data = cursor.fetchall()

    total_moyenne = 0
    total_ponderee = 0
    total_coeff = 0

    for note in notes_data:
        note_dict = {
            'id': note[0],
            'note_id': note[1],
            'matiere': note[2],
            'interrogation1': note[3] or 0,
            'interrogation2': note[4] or 0,
            'devoir': note[5] or 0,
            'coefficients': note[6] or 1
        }
        note_dict['moyenne'] = round((note_dict['interrogation1'] + note_dict['interrogation2'] + note_dict['devoir']) / 3, 2)
        moyenne_ponderee_calc = note_dict['moyenne'] * note_dict['coefficients']

        total_moyenne += note_dict['moyenne']
        total_ponderee += moyenne_ponderee_calc
        total_coeff += note_dict['coefficients']

        notes_par_matiere.append(note_dict)

    matieres_existantes = [note['matiere'] for note in notes_par_matiere]
    for matiere in matieres_fixes:
        if matiere not in matieres_existantes:
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
    response_data = {
        'etudiant': etudiant_data,
        'notes_par_matiere': notes_par_matiere,
        'moyenne_generale': moyenne_generale,
        'moyenne_ponderee': moyenne_ponderee
    }

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['PATCH'])
def api_modifier_notes_etudiant(request, etudiant_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM etudiants_user WHERE id = %s", [etudiant_id])
        etudiant = cursor.fetchone()
        
        if not etudiant:
            return Response(
                {'error': 'Étudiant non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    notes_data = request.data.get('notes', [])
    
    try:
        with connection.cursor() as cursor:
            for note in notes_data:
                matiere = note.get('matiere')
                interrogation1 = note.get('interrogation1', 0)
                interrogation2 = note.get('interrogation2', 0)
                devoir = note.get('devoir', 0)
                coefficients = note.get('coefficients', 1)
               
                cursor.execute("""
                    SELECT id FROM etudiants_notes 
                    WHERE note_id = %s AND matiere = %s
                """, [etudiant_id, matiere])
                exists = cursor.fetchone()
                
                if exists:
                    cursor.execute("""
                        UPDATE etudiants_notes 
                        SET interrogation1 = %s, interrogation2 = %s, devoir = %s, coefficients = %s
                        WHERE note_id = %s AND matiere = %s
                    """, [interrogation1, interrogation2, devoir, coefficients, etudiant_id, matiere])
                else:
                    cursor.execute("""
                        INSERT INTO etudiants_notes (note_id, matiere, interrogation1, interrogation2, devoir, coefficients)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, [etudiant_id, matiere, interrogation1, interrogation2, devoir, coefficients])

            matieres_fixes = ['Python', 'Django', 'CSS', 'Bootstrap', 'SQL']
            notes_par_matiere = []
            total_moyenne = 0
            total_ponderee = 0
            total_coeff = 0

            for matiere in matieres_fixes:
                cursor.execute("""
                    SELECT matiere, interrogation1, interrogation2, devoir, coefficients
                    FROM etudiants_notes 
                    WHERE note_id = %s AND matiere = %s
                """, [etudiant_id, matiere])
                note_data = cursor.fetchone()
                
                if note_data:
                    interrogation1, interrogation2, devoir, coefficients = note_data[1], note_data[2], note_data[3], note_data[4]
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
            
            response_data = {
                'message': 'Notes modifiées avec succès',
                'etudiant_id': etudiant_id,
                'notes_par_matiere': notes_par_matiere,
                'moyenne_generale': moyenne_generale,
                'moyenne_ponderee': moyenne_ponderee
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la modification des notes: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )