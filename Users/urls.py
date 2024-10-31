from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework.urls import path
from .views import UserViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
