from django import forms
from .models import User

class etudiantsForm(forms.Form):
    class Meta:
        model = User
        fields = ['nom', 'prenom', 'email', 'contact', 'classes']