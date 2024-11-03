from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework.urls import path
from .views import UserViewSet, InAppMessageViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'notifications', InAppMessageViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]
