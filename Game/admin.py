from django.contrib import admin

from Game.models import BattlePass, Avatar, Reward, Tier, BattlePassParticipant, DailyChallenge, \
    DailyChallengeParticipant, WeeklyChallenge, WeeklyChallengeParticipant

# Register your models here.
admin.site.register(BattlePass)
admin.site.register(Avatar)
admin.site.register(Reward)
admin.site.register(Tier)
admin.site.register(BattlePassParticipant)
admin.site.register(DailyChallenge)
admin.site.register(DailyChallengeParticipant)
admin.site.register(WeeklyChallenge)
admin.site.register(WeeklyChallengeParticipant)
