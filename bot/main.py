import asyncio
import logging
import sys

from handlers import dp
from init import set_main_menu, bot, log_error
from config import conf
from db.base import init_models
from utils.scheduler_utils import scheduler_start


async def main() -> None:
    await init_models()
    await set_main_menu()
    if not conf.debug:
        await scheduler_start()
    await dp.start_polling(bot)
    await bot.session.close()


if __name__ == "__main__":
    if conf.debug:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    else:
        log_error('start bot', with_traceback=False)
    asyncio.run(main())
