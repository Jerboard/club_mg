from init import scheduler, log_error
from apscheduler.triggers.interval import IntervalTrigger
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
    if not conf.debug:
        scheduler.add_job(check_sub, "cron", hour=21)
        scheduler.add_job(add_statistic_history, "cron", hour=00)
        scheduler.add_job(check_pay_yoo, "interval", seconds=10)
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
