import datetime

from rest_framework import serializers

from Game.models import Avatar, Tier, DailyChallengeParticipant, WeeklyChallenge, Reward, BattlePass, \
    BattlePassParticipant, DailyChallenge, WeeklyChallengeParticipant


class AvatarSerializer(serializers.ModelSerializer):
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
        return WeeklyChallengeParticipant.objects.filter(user=user, weekly_challenge=obj).exists()

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
