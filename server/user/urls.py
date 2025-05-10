from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, MessengerUserViewSet


router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'messenger-user', MessengerUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
