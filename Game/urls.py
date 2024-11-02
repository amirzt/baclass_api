from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework.urls import path
from .views import BattlePassViewSet, DailyChallengeViewSet, WeeklyChallengeViewSet, AvatarViewSet

router = DefaultRouter()
router.register(r'battlepass', BattlePassViewSet, basename='battlepass')
router.register(r'daily_challenge', DailyChallengeViewSet, basename='daily_challenge')
router.register(r'weekly_challenge', WeeklyChallengeViewSet, basename='weekly_challenge')
router.register(r'avatar', AvatarViewSet, basename='avatar')


urlpatterns = [
    path('', include(router.urls)),
]
