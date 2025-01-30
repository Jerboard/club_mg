import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import db
from config import conf
from utils.datetime_utils import months_to_months_and_days
from enums import UserStatus


async def get_statistic():
    time_start = datetime.now ()
    users = await db.get_all_users ()
    columns = ['id', 'user_id', 'full_name', 'username', 'first_visit', 'status', 'kick_date', 'alarm_2_day',
               'last_pay_id', 'recurrent', 'tariff', 'email']
    users_df = pd.DataFrame (users, columns=columns)
    users_df = users_df.set_index ('id')
    paid_users_df = users_df[users_df['status'] != UserStatus.NEW.value]

    percent_pay_users = round ((len (paid_users_df) / len (users_df)) * 100, 2)

    users_payment = await db.get_all_table_payments ()
    payment_df = pd.DataFrame(
        data=users_payment,
        columns=['id', 'user_id', 'date', 'total_amount', 'tg_payment_id', 'provider_payment_charge_id'])
    payment_df = payment_df.set_index('id')
    payment_df = payment_df[payment_df['total_amount'] == 1500]

    # Группировка по пользователю и подсчет количества оплат для каждого пользователя
    user_payments_count = payment_df.groupby ('user_id').agg ({'tg_payment_id': 'count'})

    # Получение даты последней оплаты для каждого пользователя
    user_last_payment_date = payment_df.groupby ('user_id') ['date'].max ()

    # Объединение результатов в один DataFrame
    user_payments_info = pd.merge (user_payments_count, user_last_payment_date, on='user_id')

    # Переименование столбцов
    # user_payments_info.columns = ['user_id', 'payment_count', 'last_payment_date']
    user_payments_info.columns = ['payment_count', 'last_payment_date']
    today = datetime.now ()
    thirty_days_ago = today - timedelta (days=30)
    sixty_days_ago = thirty_days_ago - timedelta (days=30)

    thirty_days_ago = pd.to_datetime(thirty_days_ago, utc=True)
    sixty_days_ago = pd.to_datetime(sixty_days_ago, utc=True)

    # Новые подписчики за последние 30 дней
    new_users_30 = user_payments_info [(user_payments_info ['last_payment_date'] >= thirty_days_ago) &
                                       (user_payments_info ['payment_count'] == 1)]
    # Продлили за последние 30 дней
    renewed_users_30 = user_payments_info [(user_payments_info ['last_payment_date'] >= thirty_days_ago) &
                                           (user_payments_info ['payment_count'] > 1)]
    # Отписались за последние 30 дней
    kick_users_30 = user_payments_info [(user_payments_info ['last_payment_date'] < thirty_days_ago) &
                                        (user_payments_info ['last_payment_date'] >= sixty_days_ago) &
                                        (user_payments_info ['payment_count'] > 0)]

    # среднее количество подписчиков за месяц
    average_followers_count_30_day = await db.get_average_followers_count ()
    # print(average_followers_count_30_day)
    percent_new_subscribers = (len (new_users_30) / average_followers_count_30_day) * 100
    percent_renewed_subscribers = (len (renewed_users_30) / average_followers_count_30_day) * 100
    percent_unsubscribed = (len (kick_users_30) / average_followers_count_30_day) * 100

    # средняя продолжительность подписки
    medium = round (user_payments_info['payment_count'].mean (), 2)
    return {
        'today': today.strftime (conf.date_format),
        "day_30_ago": thirty_days_ago.strftime (conf.date_format),
        "day_60_ago": sixty_days_ago.strftime (conf.date_format),
        'total_sub_count': len (users_df [users_df ['status'] == UserStatus.SUB.value]),
        'new_followers': len (new_users_30),
        'renewed_followers': len (renewed_users_30),
        'kick_users_count': len (kick_users_30),
        'percent_unsubscribers': round (percent_unsubscribed, 2),
        'percent_new_subscribers': round (percent_new_subscribers, 2),
        'percent_renewed_followers': round (percent_renewed_subscribers, 2),
        'medium': medium,
        'percent_pay_users': percent_pay_users
    }


async def get_statistic_text():
    statistic = await get_statistic()
    history_static = await db.get_history_static_data()

    summary = (statistic["percent_unsubscribers"] +
               statistic["percent_new_subscribers"] +
               statistic["percent_renewed_followers"])

    medium_mounts, medium_days = months_to_months_and_days(statistic['medium'])
    medium_str = f'{medium_mounts} м. {medium_days} д.'

    medium_mounts_lm, medium_days_lm = months_to_months_and_days (history_static.CTL)
    medium_lm_str = f'{medium_mounts_lm} м. {medium_days_lm} д.'

    text = f'<b>Панель администратора</b>\n\n' \
           f'<b>📊Статистика.</b>\n\n' \
           f'<b>Отчётный период:</b> \n{statistic["day_30_ago"]} - {statistic["today"]} ' \
           f'({statistic["day_60_ago"]} - {statistic["day_30_ago"]})\n' \
           f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
           f'Всего пользователей: {statistic["total_sub_count"]} ({history_static.all_users})\n' \
           f'Подписалось: {statistic["new_followers"]} ({history_static.new_sub})\n' \
           f'Продлило подписку: {statistic["renewed_followers"]} ({history_static.renewed_sub})\n' \
           f'Отписалось: {statistic["kick_users_count"]} ({history_static.unrenewed_sub})\n' \
           f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
           f'💸 Процент отписок: {statistic["percent_unsubscribers"]}% ({history_static.per_unrewed_sub}%)\n' \
           f'🧲 Процент новых подписок: {statistic["percent_new_subscribers"]}% ({history_static.per_new_sub}%)\n' \
           f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
           f'🛡 Сохранение аудитории: {statistic["percent_renewed_followers"]}% ({history_static.save_sub}%)\n' \
           f'📆 Средняя продолжительность подписки: {medium_str} ({medium_lm_str})\n' \
           f'➖➖➖➖➖➖➖➖➖➖➖➖\n' \
           f'💰 Лид -> Подписчик: {statistic["percent_pay_users"]}%\n\n\n'
           # f'⚖️ Динамическая погрешность: {round(100 - summary, 2)}% ({round(100 - history_static.error_rate, 2)}%)'

    return text


async def add_statistic_history():
    statistic = await get_statistic()

    summary = (statistic ["percent_unsubscribers"] +
               statistic ["percent_new_subscribers"] +
               statistic ["percent_renewed_followers"])

    await db.add_statistic(
        all_users=statistic['total_sub_count'],
        new_sub=statistic['new_followers'],
        renewed_sub=statistic['renewed_followers'],
        unrenewed_sub=statistic['kick_users_count'],
        per_unrewed_sub=statistic['percent_unsubscribers'],
        per_new_sub=statistic['percent_new_subscribers'],
        save_sub=statistic['percent_renewed_followers'],
        ctl=statistic['medium'],
        error_rate=100 - summary
    )
