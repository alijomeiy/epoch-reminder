from rest_framework import viewsets
from .models import Session
from .serializers import SessionSerializer


class SessionViewSet(viewsets.ModelViewSet):
    serializer_class = SessionSerializer
    queryset = Session.objects.none()

    def get_queryset(self):
        queryset = Session.objects.filter(status=Session.Status.UPCOMING)
        return queryset
