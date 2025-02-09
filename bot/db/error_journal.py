import sqlalchemy as sa
import typing as t
from datetime import datetime

from .base import METADATA, begin_connection


class ErrorJournal:
    class Row(t.Protocol):
        id: int
        created_at: datetime
        user_id: int
        error: str
        message: str
        comment: str

    Table = sa.Table(
        'error_journal',
        METADATA,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.now()),
        sa.Column('user_id', sa.Integer),
        sa.Column('error', sa.String(255)),
        sa.Column('message', sa.Text),
        sa.Column('comment', sa.Text),
    )

    @classmethod
    async def add(
            cls,
            error: str,
            message: str,
            user_id: int = None,
            comment: str = None,
    ) -> None:
        query = cls.Table.insert ().values (
            error=error[:255],
            message=message,
            user_id=user_id,
            comment=comment,
        )
        async with begin_connection () as conn:
            await conn.execute (query)

