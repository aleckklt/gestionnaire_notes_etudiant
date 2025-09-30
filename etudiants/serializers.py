from rest_framework import serializers
from .models import User, Notes

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class NotesSerializer(serializers.ModelSerializer) :
      class Meta :
            model = Notes
            fields = '__all__'