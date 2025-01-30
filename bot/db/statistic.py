import sqlalchemy as sa
import typing as t
from datetime import date, datetime, timedelta

from db.base import METADATA, begin_connection
from config import conf


class StatisticRow(t.Protocol):
    id: int
    date: date
    all_users: int
    new_sub: int
    renewed_sub: int
    unrenewed_sub: int
    per_unrewed_sub: float
    per_new_sub: float
    save_sub: float
    CTL: float
    error_rate: float


StatisticTable = sa.Table(
    'statistic',
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('date', sa.Date),
    sa.Column('all_users', sa.Integer),
    sa.Column('new_sub', sa.Integer),
    sa.Column('renewed_sub', sa.Integer),
    sa.Column('unrenewed_sub', sa.Integer),
    sa.Column('per_unrewed_sub', sa.Float),
    sa.Column('per_new_sub', sa.Float),
    sa.Column('save_sub', sa.Float),
    sa.Column('CTL', sa.Float),
    sa.Column('error_rate', sa.Float),
)


# записывает статус
async def add_statistic(
    all_users: int,
    new_sub: int,
    renewed_sub: int,
    unrenewed_sub: int,
    per_unrewed_sub: float,
    per_new_sub: float,
    save_sub: float,
    ctl: float,
    error_rate: float
) -> None:
    query = StatisticTable.insert ().values (
        date=datetime.now(conf.tz).date(),
        all_users=all_users,
        new_sub=new_sub,
        renewed_sub=renewed_sub,
        unrenewed_sub=unrenewed_sub,
        per_unrewed_sub=per_unrewed_sub,
        per_new_sub=per_new_sub,
        save_sub=save_sub,
        CTL=ctl,
        error_rate=error_rate)
    async with begin_connection () as conn:
        await conn.execute (query)


# среднее число отписок за 30 дней
async def get_average_followers_count() -> int:
    thirty_days_ago = datetime.now (conf.tz) - timedelta (days=30)

    query = sa.select(sa.func.avg(StatisticTable.c.all_users)).where(StatisticTable.c.date > thirty_days_ago.date())
    async with begin_connection () as conn:
        result = await conn.execute (query)
    return result.scalar ()


# историческая стата 30 дней назад
async def get_history_static_data() -> StatisticRow:
    target_date = datetime.now (conf.tz) - timedelta (days=30)
    query = StatisticTable.select ().where (StatisticTable.c.date == target_date.date())
    async with begin_connection () as conn:
        result = await conn.execute (query)
    return result.first ()
