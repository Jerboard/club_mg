import sqlalchemy as sa
import typing as t
from datetime import datetime

from db.base import METADATA, begin_connection
from config import conf


class UserActionJournalRow(t.Protocol):
    id: int
    time: datetime
    user_id: int
    status: str
    action: str
    comment: str


UserActionJournalTable = sa.Table(
    'action_journal',
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('time', sa.DateTime(timezone=True)),
    sa.Column('user_id', sa.BigInteger),
    sa.Column('status', sa.String(100)),
    sa.Column('action', sa.String(100)),
    sa.Column('comment', sa.Text),
)


async def reg_action(user_id: int, status: str, action: str, comment: str = None) -> None:
    query = UserActionJournalTable.insert ().values (
        # time=datetime.now(conf.tz),
        time=datetime.now(),
        user_id=user_id,
        status=status,
        action=action,
        comment=comment)
    async with begin_connection () as conn:
        await conn.execute (query)
