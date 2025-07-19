from rest_framework import serializers
from .models import User, MessengerUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "name",
            "created_by",
            "default_hezb",
            "id",
        ]


class MessengerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessengerUser
        fields = [
            "messenger_id",
        ]


class MessengerUserWithUsersSerializer(serializers.ModelSerializer):
    created_users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = MessengerUser
        fields = ["messenger_id", "created_users"]
