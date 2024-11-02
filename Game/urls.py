from rest_framework.urls import path
from .views import BattlePassViewSet

urlpatterns = [
    path('battlepass/', BattlePassViewSet.as_view({'get': 'list'})),
]
