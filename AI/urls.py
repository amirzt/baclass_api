from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework.urls import path

from AI.views import ChatViewSet

router = DefaultRouter()
router.register(r'chat', ChatViewSet, basename='chat')

urlpatterns = [
    path('', include(router.urls)),
]
