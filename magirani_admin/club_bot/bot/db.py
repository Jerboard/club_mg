from club_bot.models import ActionJournal
from club_bot.bot.base import TZ

from datetime import datetime


# добавляет действие в журнал
def reg_action(user_id: int, status: str, action: str, comment: str = None):
    new_action = ActionJournal(
        time=datetime.now(conf.tz).replace(microsecond=0),
        user_id=user_id,
        status=status,
        action=action,
        comment=comment
    )
    new_action.save()
