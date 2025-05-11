from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SessionParticipantViewSet


router = DefaultRouter()
router.register(r'participant', SessionParticipantViewSet)

urlpatterns = [
    path('', include(router.urls)),
]