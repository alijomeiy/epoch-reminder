from rest_framework import serializers
from .models import SessionParticipant


class SessionParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionParticipant
        fields = '__all__'