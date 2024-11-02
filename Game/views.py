from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from Game.models import BattlePass, BattlePassParticipant, DailyChallenge, WeeklyChallenge, Avatar
from Game.serializers import BattlePassSerializer, DailyChallengeSerializer, WeeklyChallengeSerializer, AvatarSerializer
from Users.models import CustomUser


class BattlePassViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = BattlePass.objects.all()
    serializer_class = BattlePassSerializer

    def get_queryset(self):
        self.check_participant()
        passes = BattlePass.objects.filter(is_active=True)
        return passes.order_by('-created_at')[:1]

    def get_user(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)

    def check_participant(self):
        user = self.get_user()
        battle_pass = BattlePass.objects.filter(is_active=True).order_by('-created_at').first()
        if not BattlePassParticipant.objects.filter(user=user, battle_pass=battle_pass).exists():
            BattlePassParticipant.objects.create(user=user, battle_pass=battle_pass)

    def get_serializer_class(self):
        return BattlePassSerializer

    def list(self, request, *args, **kwargs):
        battle_pass = self.get_queryset().first()
        if not battle_pass:
            return Response({"detail": "No active BattlePass found."}, status=404)
        serializer = self.get_serializer(battle_pass, context={'user': self.get_user()})
        return Response(serializer.data)


class ChallengeBaseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['battle_pass']

    def get_user(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, context={'user': self.get_user()}, many=True)
        return Response(serializer.data)


class DailyChallengeViewSet(ChallengeBaseViewSet):
    queryset = DailyChallenge.objects.all()
    serializer_class = DailyChallengeSerializer


class WeeklyChallengeViewSet(ChallengeBaseViewSet):
    queryset = WeeklyChallenge.objects.all()
    serializer_class = WeeklyChallengeSerializer


class AvatarViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Avatar.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = AvatarSerializer

    def get_user(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, context={'user': self.get_user()}, many=True)
        return Response(serializer.data)