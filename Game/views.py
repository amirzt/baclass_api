from rest_framework import status, viewsets, permissions

from Game.models import BattlePass, Tier
from Game.serializers import BattlePassSerializer


class BattlePassViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = BattlePass.objects.get(is_active=True)
    serializer_class = BattlePassSerializer

    def get_queryset(self):
        return self.queryset


