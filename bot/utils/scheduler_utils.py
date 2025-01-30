from init import scheduler

from utils.pay_utils import check_sub, check_pay_yoo
from utils.statistic_utils import add_statistic_history


# Запуск шедулеров
async def scheduler_start():
    scheduler.add_job(check_sub, "cron", hour=21)
    scheduler.add_job(add_statistic_history, "cron", hour=00)
    scheduler.add_job(check_pay_yoo, "interval", seconds=10)
    scheduler.start()
