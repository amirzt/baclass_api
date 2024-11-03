import datetime

from django.db.models import Sum

from Game.models import BattlePass, DailyChallenge, DailyChallengeParticipant, XPTracker, BattlePassParticipant, Tier, \
    WeeklyChallengeParticipant, WeeklyChallenge
from Task.models import Task
from Users.models import Student
from utils.date_functions import get_start_of_week


def calculate_level(participant):
    tiers = Tier.objects.filter(battle_pass=participant.battle_pass,
                                xp__gte=participant.xp).order_by('level')
    if not tiers.exists():
        return
    new_level = tiers.first().level
    if new_level > participant.level:
        # print('New level:', new_level)
        participant.level = new_level
        participant.save()


def add_daily_xp(user, daily, date):
    DailyChallengeParticipant.objects.create(daily_challenge=daily, user=user, date=date)
    XPTracker.objects.create(user=user, battle_pass=daily.battle_pass, xp=daily.xp)
    participant = BattlePassParticipant.objects.get(user=user, battle_pass=daily.battle_pass)
    participant.xp += daily.xp
    participant.save()
    # print(participant.xp)
    calculate_level(participant)


def check_daily_participant(user, daily, date):
    return DailyChallengeParticipant.objects.filter(daily_challenge=daily, user=user, date=date).exists()


def weekly_add(user):
    tasks = Task.objects.filter(student__user=user,
                                due_date__gte=get_start_of_week(datetime.date.today()),
                                due_date__lt=get_start_of_week(datetime.date.today()) + datetime.timedelta(
                                    days=7)).values_list('due_date').distinct()
    if tasks.count() == 7:
        battle_pass = BattlePass.objects.filter(is_active=True).first()
        weekly_challenge = WeeklyChallenge.objects.filter(battle_pass=battle_pass,
                                                          type=WeeklyChallenge.Type.every_day_add_task).first()
        if WeeklyChallengeParticipant.objects.filter(weekly_challenge=weekly_challenge,
                                                     user=user,
                                                     date=get_start_of_week(datetime.date.today())).exists():
            return
        WeeklyChallengeParticipant.objects.create(weekly_challenge=weekly_challenge,
                                                  user=user,
                                                  date=get_start_of_week(datetime.date.today()))
        XPTracker.objects.create(user=user, battle_pass=battle_pass, xp=weekly_challenge.xp)
        participant = BattlePassParticipant.objects.get(user=user, battle_pass=battle_pass)
        participant.xp += weekly_challenge.xp
        participant.save()
        print(participant.xp)
        calculate_level(participant)


def weekly_more(user):
    battle_pass = BattlePass.objects.filter(is_active=True).first()
    weekly_challenge = WeeklyChallenge.objects.filter(battle_pass=battle_pass,
                                                      type=WeeklyChallenge.Type.progress).first()
    if WeeklyChallengeParticipant.objects.filter(weekly_challenge=weekly_challenge,
                                                 user=user,
                                                 date=get_start_of_week(datetime.date.today())).exists():
        return

    current_week = Task.objects.filter(student__user=user,
                                       lesson__isnull=False,
                                       time__isnull=False,
                                       due_date__gte=get_start_of_week(datetime.date.today()),
                                       due_date__lt=get_start_of_week(datetime.date.today()) + datetime.timedelta(
                                           days=7)).aggregate(Sum('time')) or 0

    last_week = Task.objects.filter(student__user=user,
                                    lesson__isnull=False,
                                    time__isnull=False,
                                    due_date__gte=get_start_of_week(datetime.date.today()) - datetime.timedelta(
                                        days=7),
                                    due_date__lt=get_start_of_week(datetime.date.today())).aggregate(Sum('time')) or 0
    last_week = last_week['time__sum'] or 0

    if current_week['time__sum'] > last_week:
        WeeklyChallengeParticipant.objects.create(weekly_challenge=weekly_challenge,
                                                  user=user,
                                                  date=get_start_of_week(datetime.date.today()))
        XPTracker.objects.create(user=user, battle_pass=battle_pass, xp=weekly_challenge.xp)
        participant = BattlePassParticipant.objects.get(user=user, battle_pass=battle_pass)
        participant.xp += weekly_challenge.xp
        participant.save()
        print(participant.xp)
        calculate_level(participant)


def weekly_min_time(user):
    battle_pass = BattlePass.objects.filter(is_active=True).first()
    weekly_challenge = WeeklyChallenge.objects.filter(battle_pass=battle_pass,
                                                      type=WeeklyChallenge.Type.min_time).first()
    if WeeklyChallengeParticipant.objects.filter(weekly_challenge=weekly_challenge,
                                                 user=user,
                                                 date=get_start_of_week(datetime.date.today())).exists():
        return

    total_time = Task.objects.filter(student__user=user,
                                     time__isnull=False,
                                     due_date__gte=get_start_of_week(datetime.date.today()),
                                     due_date__lt=get_start_of_week(datetime.date.today()) + datetime.timedelta(
                                         days=7),
                                     lesson__isnull=False).aggregate(total_time=Sum('time'))['total_time']
    if total_time >= weekly_challenge.value:
        WeeklyChallengeParticipant.objects.create(weekly_challenge=weekly_challenge,
                                                  user=user,
                                                  date=get_start_of_week(datetime.date.today()))
        XPTracker.objects.create(user=user, battle_pass=battle_pass, xp=weekly_challenge.xp)
        participant = BattlePassParticipant.objects.get(user=user, battle_pass=battle_pass)
        participant.xp += weekly_challenge.xp
        participant.save()
        print(participant.xp)
        calculate_level(participant)


def calculate_score(user, category, **kwargs):
    battle_pass = BattlePass.objects.filter(is_active=True).first()
    student = Student.objects.get(user=user)

    if not battle_pass:
        return
    if category == 'add_task':
        weekly_add(user)
        daily = DailyChallenge.objects.get(type=DailyChallenge.Type.add_task,
                                           battle_pass=battle_pass)
        if check_daily_participant(user, daily, kwargs['due_date']):
            return
        tasks_count = Task.objects.filter(student=student, due_date=kwargs['due_date']).count()

        if tasks_count >= daily.value:
            add_daily_xp(user, daily, kwargs['due_date'])
        return

    if category == 'complete_task':
        daily = DailyChallenge.objects.get(type=DailyChallenge.Type.complete_task,
                                           battle_pass=battle_pass)
        if not check_daily_participant(user, daily, kwargs['due_date']):
            tasks_count = Task.objects.filter(student=student, due_date=kwargs['due_date'], is_done=True).count()

            if tasks_count >= daily.value:
                add_daily_xp(user, daily, kwargs['due_date'])

        # calculate daily min time
        total_time = Task.objects.filter(student=student, due_date=kwargs['due_date'], is_done=True,
                                         lesson__isnull=False).aggregate(total_time=Sum('time'))['total_time']

        daily = DailyChallenge.objects.get(type=DailyChallenge.Type.min_time,
                                           battle_pass=battle_pass)
        if not check_daily_participant(user, daily, kwargs['due_date']):
            if total_time >= daily.value:
                add_daily_xp(user, daily, kwargs['due_date'])

        # calculate more than last week
        weekly_more(user)

        # calculate weekly min time
        weekly_min_time(user)

    if category == 'open_app':
        daily = DailyChallenge.objects.get(type=DailyChallenge.Type.open_app,
                                           battle_pass=battle_pass)
        if check_daily_participant(user, daily, datetime.date.today()):
            return
        add_daily_xp(user, daily, datetime.date.today())
        return
