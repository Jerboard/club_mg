from aiogram import Dispatcher
from aiogram.types.bot_command import BotCommand
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from yookassa import Configuration

from datetime import datetime

import asyncio
import logging
import traceback
import redis
import os
import re

from sqlalchemy.ext.asyncio import create_async_engine
from config import conf

import asyncio
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except:
    pass


loop = asyncio.get_event_loop()
dp = Dispatcher()
bot = Bot(conf.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Настройка Redis
redis_client = redis.StrictRedis(host=conf.redis_host, port=conf.redis_port, db=0)


scheduler = AsyncIOScheduler(
    timezone=conf.tz_utc,
    jobstores={
        'default': RedisJobStore(host=conf.redis_host, port=conf.redis_port, db=1)
    },
    executors={
        'default': AsyncIOExecutor()
    },
    job_defaults={
        'coalesce': True,
        'max_instances': 3
    }
)

redis_client_1 = redis.StrictRedis(host=conf.redis_host, port=conf.redis_port, db=1)


ENGINE = create_async_engine(url=conf.db_url)

Configuration.account_id = conf.yoo_account_id
Configuration.secret_key = conf.yoo_secret_key


async def set_main_menu():
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Перезапустить')
    ]

    await bot.set_my_commands(main_menu_commands)


def log_error(message, with_traceback: bool = True) -> tuple[str, str]:
    now = datetime.now(conf.tz)
    log_folder = now.strftime ('%m-%Y')
    log_path = os.path.join('logs', log_folder)

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    log_file_path = os.path.join(log_path, f'{now.day}.log')
    logging.basicConfig (level=logging.WARNING, filename=log_file_path, encoding='utf-8')
    if with_traceback:
        ex_traceback = traceback.format_exc()
        tb = ''
        msg = ''
        start_row = '  File "/app'
        tb_split = ex_traceback.split('\n')
        for row in tb_split:
            if row.startswith(start_row) and not re.search ('venv', row):
                tb += f'{row}\n'

            if not row.startswith(' '):
                msg += f'{row}\n'

        logging.warning(f'{now}\n{tb}\n\n{msg}\n---------------------------------\n')
        return tb, msg
    else:
        logging.warning(f'{now}\n{message}\n\n---------------------------------\n')
        return message

