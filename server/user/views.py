from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from .models import User, MessengerUser
from .serializers import UserSerializer, MessengerUserSerializer, MessengerUserWithUsersSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        messenger_id = request.data.get("created_by")
        messenger_user = MessengerUser.objects.get(messenger_id=messenger_id)
        request.data["created_by"] = messenger_user.id
        return super().create(request, *args, **kwargs)


# class MessengerUserViewSet(viewsets.ModelViewSet):
#     queryset = MessengerUser.objects.all()
#     serializer_class = MessengerUserSerializer


class MessengerUserViewSet(viewsets.ModelViewSet):
    queryset = MessengerUser.objects.all()
    serializer_class = MessengerUserWithUsersSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=["get"])
    def users(self, request, pk=None):
        messenger_user = MessengerUser.objects.filter(messenger_id=pk).first()
        users = User.objects.filter(created_by=messenger_user)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
