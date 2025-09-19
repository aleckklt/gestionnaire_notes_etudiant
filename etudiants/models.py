from django.db import models
from django.utils import timezone


class User(models.Model) :
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact = models.TextField(max_length=15, blank=True, null=True)
    is_valid = models.BooleanField(default=False, null=True)

    def __str__(self) :
        return f"{self.nom} {self.prenom}"

    class Meta :
        ordering = ["-nom"]

class notes(models.Model):
    MATIERE_CHOICES = [
        ('Django', 'Django'),
        ('Python', 'Python'),
        ('CSS', 'CSS'),
        ('Bootstrap', 'Bootstrap'),
        ('SQL', 'SQL'),
    ]

    note = models.ForeignKey(User, on_delete=models.CASCADE)
    matiere = models.CharField(max_length=20, choices=MATIERE_CHOICES)
    interrogation = models.FloatField(null=True, blank=True)
    devoir = models.FloatField(null=True, blank=True)
    devoirs = models.FloatField(null=True, blank=True)
    coefficent = models.PositiveIntegerField(default=1)
    date_note = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.etudiant} - {self.matiere}"