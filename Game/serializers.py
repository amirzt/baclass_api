import datetime

from rest_framework import serializers

from Game.models import Avatar, Tier, DailyChallengeParticipant, WeeklyChallenge, Reward, BattlePass, \
    BattlePassParticipant, DailyChallenge, WeeklyChallengeParticipant, AvatarOwnerShip
from Users.models import CustomUser
from Users.serializers import CustomUserSerializer
from utils.date_functions import get_start_of_week


class AvatarSerializer(serializers.ModelSerializer):
    is_owned = serializers.SerializerMethodField('get_owned')

    def get_owned(self, obj):
        if 'user' not in self.context:
            return False
        return AvatarOwnerShip.objects.filter(avatar=obj,
                                              user=self.context.get('user')).exists()

    class Meta:
        model = Avatar
        fields = '__all__'


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = '__all__'


class TierSerializer(serializers.ModelSerializer):
    reward = RewardSerializer()

    class Meta:
        model = Tier
        fields = '__all__'


class DailyChallengeSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField('get_is_completed')

    def get_is_completed(self, obj):
        user = self.context['user']
        return DailyChallengeParticipant.objects.filter(user=user, daily_challenge=obj,
                                                        date=datetime.date.today()).exists()

    class Meta:
        model = DailyChallenge
        fields = '__all__'


class WeeklyChallengeSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField('get_is_completed')

    def get_is_completed(self, obj):
        user = self.context['user']
        return WeeklyChallengeParticipant.objects.filter(user=user,
                                                         weekly_challenge=obj,
                                                         date=get_start_of_week(datetime.date.today())).exists()

    class Meta:
        model = WeeklyChallenge
        fields = '__all__'


class BattlePassParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = BattlePassParticipant
        fields = '__all__'


class BattlePassSerializer(serializers.ModelSerializer):
    tiers = serializers.SerializerMethodField('get_tiers')
    user_level = serializers.SerializerMethodField('get_user_level')

    @staticmethod
    def get_tiers(self):
        # return []
        all_tiers = Tier.objects.filter(battle_pass=self).order_by('level')
        serializer = TierSerializer(all_tiers, many=True)
        return serializer.data

    def get_user_level(self, obj):
        user = self.context.get('user')
        if user:
            participant = BattlePassParticipant.objects.get(user=user, battle_pass=obj)
            return BattlePassParticipantSerializer(participant).data
        return None

    class Meta:
        model = BattlePass
        fields = '__all__'


class UserWithXPSerializer(serializers.Serializer):
    total_xp = serializers.IntegerField()
    user = serializers.SerializerMethodField('get_user')

    @staticmethod
    def get_user(self):
        return CustomUserSerializer(CustomUser.objects.get(id=self['user'])).data
