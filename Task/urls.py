from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework.urls import path

from . import views
from .views import TaskViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]