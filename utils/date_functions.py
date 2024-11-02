import datetime


def get_start_of_week(today):
    start_of_week = today - datetime.timedelta(days=(today.weekday() + 2) % 7)
    return start_of_week
