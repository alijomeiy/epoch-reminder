from rest_framework import viewsets
from .models import User, MessengerUser
from .serializers import UserSerializer, MessengerUserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        # Get the messenger_id from request data
        messenger_id = request.data.get('created_by')
        print("\n\nMESSENGER ID: ", messenger_id)
        # Get or create MessengerUser
        messenger_user = MessengerUser.objects.get(messenger_id=messenger_id)
        # Update request data with MessengerUser id
        print("\n\n1. REQUEST DATA: ", request.data)
        request.data['created_by'] = messenger_user.id
        print("\n\n2. REQUEST DATA: ", request.data)
        return super().create(request, *args, **kwargs)


class MessengerUserViewSet(viewsets.ModelViewSet):
    queryset = MessengerUser.objects.all()
    serializer_class = MessengerUserSerializer