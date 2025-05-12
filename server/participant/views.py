from rest_framework import viewsets
from .models import SessionParticipant
from .serializers import SessionParticipantSerializer


class SessionParticipantViewSet(viewsets.ModelViewSet):
    queryset = SessionParticipant.objects.all()
    serializer_class = SessionParticipantSerializer
