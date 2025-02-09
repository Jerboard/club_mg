from datetime import date, timedelta, datetime, time
from dateutil.relativedelta import relativedelta

import typing as t

from config import conf


# добавить месяцы по 30 дней
def add_months(count_months: int, kick_date: date = None):
    today = datetime.now(conf.tz).date()
    if not kick_date or kick_date < today:
        kick_date = today

    while count_months > 0:
        kick_date = kick_date + timedelta (days=30)
        count_months -= 1

    return kick_date


# Функция вычитания месяцев из текущей даты
def minus_months(count_months: int) -> datetime.date:
    today = datetime.now(conf.tz).date()
    # Используем relativedelta для безопасного вычитания месяцев
    new_date = today - relativedelta(months=count_months)

    # Проверяем корректность последнего дня месяца
    if new_date.day != today.day:
        last_day_of_new_month = (new_date.replace(day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        new_date = new_date.replace(day=min(today.day, last_day_of_new_month.day))

    return new_date


# вычесть месяцы из сегодня по месяцу
# def minus_months(count_mounts: int) -> date:
#     today = datetime.now(conf.tz).date()
#     new_day = today.day
#     new_mount = today.month - count_mounts
#     # new_mount = count_mounts % 12
#     new_year = today.year
#
#     if new_mount < 1:
#         new_mount = 12 + new_mount
#         new_year -= count_mounts // 12
#
#     if new_day > 28 and new_mount == 2:
#         new_day = 28
#
#     elif new_day > 30 and new_mount in [4, 6, 9, 11]:
#         new_day = 30
#
#     return datetime.strptime(f'{new_day}.{new_mount}.{new_year}', DATE_FORMAT).date()


# превращает десятичное число в количество дней и месяцев
def months_to_months_and_days(total_months):
    # Преобразование общего количества месяцев в количество месяцев и дней
    months = total_months // 1  # Целое количество месяцев
    remaining_days = round((total_months % 1) * 30)  # Оставшиеся дни, округленные до ближайшего целого

    return int(months), remaining_days


# определяет следующую дату старта
def get_next_start_date(next_start_date: date, next_start_time: time) -> datetime:
    return datetime.combine(next_start_date, next_start_time, tzinfo=conf.tz)