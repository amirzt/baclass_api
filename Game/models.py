from django.db import models

from Users.models import Student, CustomUser


class Avatar(models.Model):
    image = models.ImageField(upload_to='Avatars/')
    name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    price = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Reward(models.Model):
    class Type(models.TextChoices):
        coin = 'coin', 'Coin'
        avatar = 'avatar', 'Avatar'

    coin = models.IntegerField(default=0)
    avatar = models.ForeignKey(Avatar, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.coin)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type


class BattlePass(models.Model):
    title = models.CharField(max_length=1000)
    description = models.TextField(max_length=1000)
    is_active = models.BooleanField(default=True)

    start_date = models.DateField()
    end_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Tier(models.Model):
    battle_pass = models.ForeignKey(BattlePass, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, null=True, blank=True)
    level = models.IntegerField(default=0)
    xp = models.IntegerField(default=0)
    reward = models.ForeignKey(Reward, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BattlePassParticipant(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    battle_pass = models.ForeignKey(BattlePass, on_delete=models.CASCADE)
    level = models.IntegerField(default=0)
    xp = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'battle_pass')


class DailyChallenge(models.Model):
    class Type(models.TextChoices):
        add_task = 'add_task', 'Add Task'
        complete_task = 'complete_task', 'Complete Task'
        open_app = 'open_app', 'Open App'
        min_time = 'min_time', 'Min Time'
        different_lesson = 'different_lesson', 'Different Lesson'

    battle_pass = models.ForeignKey(BattlePass, on_delete=models.CASCADE)

    title = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(max_length=1000)
    type = models.CharField(max_length=50, choices=Type.choices, default=Type.add_task)

    xp = models.IntegerField(default=0)
    value = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DailyChallengeParticipant(models.Model):
    daily_challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    date = models.DateField(null=False)


class WeeklyChallenge(models.Model):
    class Type(models.TextChoices):
        min_time = 'min_time', 'MinTime'
        every_day_enter = 'every_day_enter', 'Every Day Enter'
        every_day_add_task = 'every_day_add_task', 'Every Day Add Task'
        progress = 'progress', 'Progress'

    battle_pass = models.ForeignKey(BattlePass, on_delete=models.CASCADE)

    title = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(max_length=1000)
    type = models.CharField(max_length=50, choices=Type.choices, default=Type.min_time)

    xp = models.IntegerField(null=False)
    value = models.IntegerField(default=0)


class WeeklyChallengeParticipant(models.Model):
    weekly_challenge = models.ForeignKey(WeeklyChallenge, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    date = models.DateField(null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class XPTracker(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    battle_pass = models.ForeignKey(BattlePass, on_delete=models.CASCADE)
    xp = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)