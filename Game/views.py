from datetime import timedelta

from django.db.models import Sum, Q, OuterRef, Subquery
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Game.models import BattlePass, BattlePassParticipant, DailyChallenge, WeeklyChallenge, Avatar, XPTracker
from Game.serializers import BattlePassSerializer, DailyChallengeSerializer, WeeklyChallengeSerializer, \
    AvatarSerializer, UserWithXPSerializer
from Users.models import CustomUser
from Users.serializers import CustomUserSerializer


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

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def ranking(self, request):
        battle_pass = self.get_queryset().first()
        filter_date = timezone.now() - timedelta(days=30)

        if 'period' in request.query_params:
            period = request.query_params['period']
            if period == 'week':
                filter_date = timezone.now() - timedelta(days=7)
            elif period == 'month':
                filter_date = timezone.now() - timedelta(days=30)
            else:
                filter_date = battle_pass.start_date

        # Filter XPTracker records for the specific BattlePass and time range
        # Get participants for the specified BattlePass
        xp_subquery = XPTracker.objects.filter(
            user=OuterRef('user'),
            battle_pass=battle_pass,
            created_at__gte=filter_date
        ).values('user').annotate(total_xp=Sum('xp')).values('total_xp')

        # Get participants for the specified BattlePass and annotate with total XP from the subquery
        users_with_xp = (
            BattlePassParticipant.objects
            .filter(battle_pass=battle_pass)
            .annotate(total_xp=Subquery(xp_subquery))
            .order_by('-total_xp')  # Sort by total XP descending
            .values('user', 'total_xp')  # Select only user ID and total XP
        )
        serializer = UserWithXPSerializer(users_with_xp, many=True)
        return Response(status=200, data=serializer.data)


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
