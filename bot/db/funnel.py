import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
import typing as t
from datetime import datetime, date, time

from .base import METADATA, begin_connection
from .saved_messages import SaveMessagesTable
from config import conf


class Funnel:
    class Row(t.Protocol):
        id: int
        created_at: datetime
        updated_at: datetime
        # next_start: datetime
        next_start_date: date
        next_start_time: time
        user_id: int
        save_msg_id: int
        period_day: int
        # time_sending: str
        group_recip: str
        period_id: int
        is_active: bool

    class FullRow(t.Protocol):
        funnel_id: int
        created_at: datetime
        updated_at: datetime
        # next_start: datetime
        next_start_date: date
        next_start_time: time
        user_id: int
        save_msg_id: int
        period_day: int
        # time_sending: str
        is_active: bool
        title: str
        text: str
        entities: str
        photo: str
        group_recip: str
        period_id: int

    Table = sa.Table(
        'funnel',
        METADATA,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        # sa.Column('next_start', sa.DateTime(timezone=True)),
        sa.Column('next_start_date', sa.Date()),
        sa.Column('next_start_time', sa.Time()),
        sa.Column('save_msg_id', sa.Integer),
        sa.Column('user_id', sa.Integer),
        sa.Column('period_day', sa.Integer, default=0),
        # sa.Column('time_sending', sa.String(5)),
        sa.Column('group_recip', sa.String(255)),
        sa.Column('period_id', sa.Integer),
        sa.Column('is_active', sa.Boolean, default=False)
    )

    @classmethod
    def get_join_query(cls) -> sa.Select:
        return (
            sa.select(
                cls.Table.c.id.label('funnel_id'),
                cls.Table.c.created_at,
                cls.Table.c.updated_at,
                cls.Table.c.next_start_date,
                cls.Table.c.next_start_time,
                cls.Table.c.user_id,
                cls.Table.c.save_msg_id,
                cls.Table.c.period_day,
                # cls.Table.c.time_sending,
                cls.Table.c.is_active,
                cls.Table.c.group_recip,
                cls.Table.c.period_id,
                SaveMessagesTable.c.title,
                SaveMessagesTable.c.text,
                SaveMessagesTable.c.entities,
                SaveMessagesTable.c.photo,
            ).select_from(
                cls.Table.join(
                    SaveMessagesTable,
                    SaveMessagesTable.c.id == cls.Table.c.save_msg_id,
                    isouter=True
                ),
            )
        )

    @classmethod
    async def add(
            cls,
            save_msg_id: int,
            group_recip: str,
            period_id: int,
            user_id: int
    ) -> int:
        now = datetime.now(conf.tz)
        query = cls.Table.insert ().values (
            created_at=now,
            updated_at=now,
            # next_start=now,
            next_start_date=now.date(),
            next_start_time=now.time(),
            save_msg_id=save_msg_id,
            # time_sending=time_sending,
            group_recip=group_recip,
            period_id=period_id,
            user_id=user_id,
        )
        async with begin_connection () as conn:
            result = await conn.execute (query)

        return result.inserted_primary_key[0]

    @classmethod
    async def edit(
            cls,
            funnel_id: int,
            period_day: int = None,
            # time_sending: str = None,
            # next_start_date: datetime = None,
            next_start_date: date = None,
            next_start_time: time = None,
            is_active: bool = None,
    ) -> None:
        now = datetime.now(conf.tz)

        query = cls.Table.update ().where(cls.Table.c.id == funnel_id).values(updated_at=now)

        if is_active is not None:
            query = query.values(is_active=is_active)
        if period_day:
            query = query.values(period_day=period_day)
        # if time_sending:
        #     query = query.values(time_sending=time_sending)
        if next_start_date:
            query = query.values(next_start_date=next_start_date)
        if next_start_time:
            query = query.values(next_start_time=next_start_time)

        async with begin_connection () as conn:
            await conn.execute (query)

    @classmethod
    async def get(cls) -> list[FullRow]:
        query = cls.get_join_query()

        async with begin_connection () as conn:
            result = await conn.execute (query)

        return result.all()

    @classmethod
    async def get_by_id(cls, funnel_id: int) -> FullRow:
        query = cls.get_join_query()
        query = query.where(cls.Table.c.id == funnel_id)

        async with begin_connection () as conn:
            result = await conn.execute (query)

        return result.first()

    @classmethod
    async def del_funnel(cls, funnel_id: int) -> None:
        query = cls.Table.delete().where(cls.Table.c.id == funnel_id)

        async with begin_connection () as conn:
            await conn.execute (query)
