import asyncio
import logging
import sys

from datetime import datetime

from handlers import dp
from init import set_main_menu, bot, log_error
from config import conf
from db.base import init_models
from utils.scheduler_utils import scheduler_start, scheduler_stop


async def main() -> None:
    await init_models()
    await set_main_menu()
    if not conf.debug:
        await scheduler_start()
    else:
        pass
        await scheduler_start()
    await dp.start_polling(bot)
    await scheduler_stop()
    await bot.session.close()


if __name__ == "__main__":
    if conf.debug:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    else:
        log_error('start bot', with_traceback=False)
    asyncio.run(main())
