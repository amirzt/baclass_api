from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework.urls import path

from Shop.views import PackageViewSet

router = DefaultRouter()
router.register(r'package', PackageViewSet, basename='package')

urlpatterns = [
    path('', include(router.urls)),
]
