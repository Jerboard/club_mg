from init import scheduler, log_error, redis_client_1
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta, date, time
from random import randint

from config import conf
import db
from db.funnel import Funnel
from data.base_data import periods
from .pay_utils import check_sub, check_pay_yoo
from .statistic_utils import add_statistic_history
from .datetime_utils import get_next_start_date
from .message_utils import get_milling_user_list, mailing


# Запуск шедулеров
async def scheduler_start():
    # if not conf.debug:
    scheduler.add_job(
        check_sub,
        CronTrigger(hour=21),
        id='check_sub',
        replace_existing=True
    )
    scheduler.add_job(
        add_statistic_history,
        CronTrigger(hour=0),
        id='add_statistic_history',
        replace_existing=True
    )
    scheduler.add_job(
        check_pay_yoo,
        IntervalTrigger(seconds=10),
        id='check_pay_yoo',
        replace_existing=True
    )

    await check_redis_keys()

    scheduler.start()


async def funnel_malling(funnel_id: int):
    try:
        funnel = await Funnel.get_by_id(funnel_id=funnel_id)

        user_period: dict = periods[funnel.period_id]

        if conf.debug:
            users = await db.get_all_users()

        else:
            users = await get_milling_user_list(
                unit=user_period['unit'],
                group_recip=funnel.group_recip,
                start=user_period['start'],
                end=user_period['end']
            )

        await mailing(
            chat_id=funnel.user_id,
            users=users,
            text=funnel.text,
            entities_str=funnel.entities,
            photo=funnel.photo,
        )
    except Exception as ex:
        log_error(ex)


# создаёт воронку
async def add_funnel_job(funnel_id: int):
    funnel = await Funnel.get_by_id(funnel_id)

    next_start = get_next_start_date(next_start_date=funnel.next_start_date, next_start_time=funnel.next_start_time)

    now = datetime.now(conf.tz)
    if next_start < now:
        start_date = next_start
    else:
        new_date = now + timedelta(days=funnel.period_day)
        start_date = get_next_start_date(next_start_date=new_date.date(), next_start_time=funnel.next_start_time)
        await Funnel.edit(funnel_id=funnel_id, next_start_date=start_date.date())

    scheduler.add_job(
        funnel_malling,
        IntervalTrigger(days=funnel.period_day, start_date=start_date),
        id=f"funnel-{funnel.funnel_id}",
        replace_existing=True,
        args=(funnel.funnel_id,)
    )


# создаёт воронку
async def del_funnel_job(funnel_id: int):
    try:
        scheduler.remove_job(job_id=f"funnel-{funnel_id}")
        # jods = scheduler.get_jobs()
        # for j in jods:
        #     scheduler.remove_job(job_id=j.id)
    except:
        pass


# проверяет ключи
async def check_redis_keys():
    try:
        print('🔍 Ключи в Redis (db=1):')
        keys_tts = redis_client_1.keys("*")

        for key in keys_tts:
            key = key.decode()  # Декодируем ключ в строку
            key_type = redis_client_1.type(key).decode()  # Определяем тип ключа
            print(f"\n🔹 Ключ: {key} (Тип: {key_type})")

            if key_type == "string":
                value = redis_client_1.get(key).decode()
                print(f"📜 Значение (string): {value}")

            elif key_type == "hash":
                value = redis_client_1.hgetall(key)
                decoded_value = {}
                for k, v in value.items():
                    try:
                        decoded_value[k.decode()] = v.decode()
                    except UnicodeDecodeError:
                        decoded_value[k.decode()] = 'v'  # Оставляем в байтах
                print(f"📦 Значение (hash): {decoded_value}")

            elif key_type == "list":
                value = [v.decode() for v in redis_client_1.lrange(key, 0, -1)]
                print(f"📋 Значение (list): {value}")

            elif key_type == "set":
                value = {v.decode() for v in redis_client_1.smembers(key)}
                print(f"🔢 Значение (set): {value}")

            elif key_type == "zset":
                for v, score in redis_client_1.zrange(key, 0, -1, withscores=True):
                    try:
                        values = v.decode(), datetime.fromtimestamp(score, conf.tz).strftime(conf.datetime_format)
                    except:
                        values = v.decode(), score

                    print(f"🏆 Значение: {values}")

            else:
                print("⚠️ Неизвестный тип данных, попробуйте исследовать вручную.")

    except Exception as ex:
        log_error(ex)
