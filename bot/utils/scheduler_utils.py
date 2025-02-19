from init import scheduler, log_error, redis_client_1
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta, date, time, timezone
from random import randint

import logging
import pickle


from config import conf
import db
from db.funnel import Funnel
from data.base_data import periods
from .pay_utils import check_sub, check_pay_yoo
from .statistic_utils import add_statistic_history
from .datetime_utils import get_next_start_date
from .message_utils import get_milling_user_list, mailing
from enums import JobName, job_name_list


# Запуск шедулеров
async def scheduler_start():
    if not conf.debug:
        scheduler.add_job(
            check_sub,
            CronTrigger(hour=18),
            id=JobName.CHECK_SUB.value,
            replace_existing=True
        )
        scheduler.add_job(
            add_statistic_history,
            CronTrigger(hour=21),
            id=JobName.ADD_STATISTIC.value,
            replace_existing=True
        )
        scheduler.add_job(
            check_pay_yoo,
            IntervalTrigger(seconds=10),
            id=JobName.CHECK_PAY_YOO.value,
            replace_existing=True
        )

    scheduler.start()
    get_scheduled_jobs()


# останавливает планировщики
async def scheduler_stop():
    for job in job_name_list:
        try:
            scheduler.remove_job(job)
        except Exception as ex:
            pass


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


def get_scheduled_jobs():
    """Получает все задачи APScheduler из Redis и выводит их время выполнения в UTC."""
    jobs = redis_client_1.hgetall("apscheduler.jobs")

    if not jobs:
        text = "⛔ В Redis нет задач APScheduler."
        log_error(text, with_traceback=False)
        return

    text = "📅 Запланированные задачи в UTC:\n"
    for job_id, job_data in jobs.items():
        try:
            job = pickle.loads(job_data)  # Десериализация данных
            job_next_run = job.get("next_run_time")  # Дата следующего выполнения

            if job_next_run:
                # Приводим время к UTC (если оно не в UTC)
                job_next_run = job_next_run.astimezone(timezone.utc)
                next_run_str = job_next_run.strftime("%Y-%m-%d %H:%M:%S UTC")
            else:
                next_run_str = "Не запланировано"

            text += (
                f"🔹 Задача ID: {job_id.decode()}\n"
                f"  ➜ Функция: {job['func']}\n"
                f"  ➜ Следующее выполнение: {next_run_str}\n"
            )

        except Exception as e:
            text += f"⚠️ Ошибка при декодировании задачи {job_id.decode()}: {e}\n"

    log_error(text, with_traceback=False)
