import sqlalchemy as sa
import typing as t
from datetime import datetime, timedelta

from .base import METADATA, begin_connection


class MailJournal:
    class Row(t.Protocol):
        id: int
        created_at: datetime
        all_msg: int
        success: int
        failed: int
        blocked: int
        unblocked: int
        time_mailing: timedelta
        report: str

    Table = sa.Table(
        'mailing_journal',
        METADATA,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.now()),
        sa.Column('all_msg', sa.Integer),
        sa.Column('success', sa.Integer),
        sa.Column('failed', sa.Integer),
        sa.Column('blocked', sa.Integer),
        sa.Column('unblocked', sa.Integer),
        sa.Column('time_mailing', sa.Interval),
        sa.Column('report', sa.Text),
    )

    @classmethod
    async def add(
            cls,
            all_msg: int,
            success: int,
            failed: int,
            blocked: int,
            unblocked: int,
            time_mailing: timedelta,
            report: str
    ) -> None:
        query = cls.Table.insert ().values (
            all_msg=all_msg,
            success=success,
            failed=failed,
            blocked=blocked,
            unblocked=unblocked,
            time_mailing=time_mailing,
            report=report
        )
        async with begin_connection () as conn:
            await conn.execute (query)