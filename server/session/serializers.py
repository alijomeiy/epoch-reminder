from rest_framework import serializers
from .models import Session


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['id', 'start_time', 'end_time', 'start_register_time', 'end_register_time', 'status']
