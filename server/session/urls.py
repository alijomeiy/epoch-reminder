from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SessionViewSet


router = DefaultRouter()
router.register(r'session', SessionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
