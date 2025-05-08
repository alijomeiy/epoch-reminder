from rest_framework import viewsets
from .models import User, MessengerUser
from .serializers import UserSerializer, MessengerUserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class MessengerUserViewSet(viewsets.ModelViewSet):
    queryset = MessengerUser.objects.all()
    serializer_class = MessengerUserSerializer
