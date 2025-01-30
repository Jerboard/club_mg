from aiogram.types import ErrorEvent, Message

from init import dp, bot, log_error
from config import conf


if not conf.debug:
    @dp.errors()
    async def error_handler(ex: ErrorEvent):
        log_error (ex)
        # if ex.update.message:
        #     log_error (ex.exception)
        #
        #     text = 'Перезапустите сессию /start'
        #     await bot.send_message(chat_id=ex.update.message.chat.id, text=text)
        #
        # else:
        #     log_error(ex.exception)
