from django.db import models
from django.utils import timezone

class User(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=15, blank=True, null=True)
    is_valid = models.BooleanField(default=False, null=True)

    def __str__(self):
        return f"{self.nom} {self.prenom}"

    class Meta:
        ordering = ["-nom"]
        
class Notes(models.Model):
    note = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    interrogation1 = models.FloatField(null=True, blank=True)
    interrogation2 = models.FloatField(null=True, blank=True)
    devoir = models.FloatField(null=True, blank=True)
    matiere = models.CharField(max_length=25, blank=True, null=True)
    coefficients = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.note} - {self.matiere}"