from aiogram.types import ErrorEvent, Message

from db.error_journal import ErrorJournal
from init import dp, bot, log_error
from config import conf


# if not conf.debug:
@dp.errors()
async def error_handler(ex: ErrorEvent):
    tb, msg = log_error (ex)
    user_id = ex.update.message.from_user.id if ex.update.message else None

    await ErrorJournal.add(
        error=msg.replace('Traceback (most recent call last):', '').strip(),
        message=tb,
        user_id=user_id
    )
