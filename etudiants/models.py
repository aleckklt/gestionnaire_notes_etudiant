from django.db import models

class User(models.Model) :
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.TextField(blank=True, null=True)
    classes = models.TextField(blank=True, null=True)
    is_valid = models.BooleanField(default=False, null=True)

    def __str__(self) :
        self.nom

    class Meta :
        ordering = ["-nom"]

class notes(models.Model):
    note = models.ForeignKey(User, on_delete= models.CASCADE)
    noted = models.IntegerField()
    noted_by = models.BooleanField(default=False)
    note_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        self.note