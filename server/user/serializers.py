from rest_framework import serializers
from .models import User, MessengerUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'created_by', 'default_hezb']


class MessengerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessengerUser
        fields = ['messenger_id', ]
