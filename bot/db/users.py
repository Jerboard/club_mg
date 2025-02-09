import sqlalchemy as sa
import typing as t

from sqlalchemy.dialects import postgresql as psql
from datetime import date, datetime

from config import conf
from db.base import METADATA, begin_connection
from enums import UserStatus


class UserRow(t.Protocol):
    id: int
    user_id: int
    full_name: str
    username: str
    first_visit: date
    status: str
    kick_date: date
    alarm_2_day: bool
    last_pay_id: str
    recurrent: bool
    tariff: str
    email: str
    is_blocked: bool


UserTable = sa.Table(
    'users',
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('user_id', sa.BigInteger),
    sa.Column('full_name', sa.String(255)),
    sa.Column('username', sa.String(255)),
    sa.Column('first_visit', sa.Date),
    sa.Column('status', sa.String(255)),
    sa.Column('kick_date', sa.Date),
    sa.Column('alarm_2_day', sa.Boolean, default=False),
    sa.Column('last_pay_id', sa.String(255)),
    sa.Column('recurrent', sa.Boolean, default=False),
    sa.Column('tariff', sa.String(255)),
    sa.Column('email', sa.String(255)),
    sa.Column('is_blocked', sa.Boolean, default=False),
)


# данные пользователя
async def get_user_info(user_id: int = None, email: str = None) -> UserRow:
    query = UserTable.select ()
    if user_id:
        query = query.where (UserTable.c.user_id == user_id)
    if email:
        query = query.where (UserTable.c.email == email.lower())
    async with begin_connection () as conn:
        result = await conn.execute (query)
    return result.first ()


# сохраняет транзакцию
async def add_user(user_id: int, full_name: str, username: str) -> None:
    query = psql.insert(UserTable).values(
        user_id=user_id,
        full_name=full_name,
        username=username,
        first_visit=datetime.now(conf.tz).date(),
        status=UserStatus.NEW.value
    )
    async with begin_connection () as conn:
        await conn.execute (query)


# вся таблица users
async def get_all_users(status: str = None, target_date: date = None) -> tuple[UserRow]:
    query = UserTable.select ()
    if status:
        query = query.where(UserTable.c.status == status)

    if target_date:
        query = query.where(UserTable.c.kick_date < target_date)

    async with begin_connection () as conn:
        result = await conn.execute (query)
    return result.all ()


async def update_user_info(
        user_id: int,
        full_name: str = None,
        username: str = None,
        email: str = None,
        recurrent: bool = None,
        status: str = None,
        kick_date: date = None,
        last_pay_id: str = None,
        alarm_2_day: bool = None,
        is_blocked: bool = None,
        tariff: str = None,
) -> None:
    query = UserTable.update ().where(UserTable.c.user_id == user_id)

    if full_name:
        query = query.values(full_name=full_name)
    if username:
        query = query.values(username=username)
    if email:
        query = query.values(email=email.lower())
    if recurrent is not None:
        query = query.values (recurrent=recurrent)
    if status:
        query = query.values(status=status)
    if kick_date:
        query = query.values(kick_date=kick_date)
    if last_pay_id:
        query = query.values(last_pay_id=last_pay_id)
    if tariff:
        query = query.values(tariff=tariff)
    if alarm_2_day is not None:
        query = query.values (alarm_2_day=alarm_2_day)
    if is_blocked is not None:
        query = query.values (is_blocked=is_blocked)

    async with begin_connection () as conn:
        await conn.execute (query)


# удаляет строку пользователя
async def delete_user_empty(empty_id: int) -> None:
    query = UserTable.delete ().where (UserTable.c.id == empty_id)
    async with begin_connection () as conn:
        await conn.execute (query)


async def add_email_wo_user(email: str, tariff: str, pay_method) -> None:
    query = UserTable.insert ().values (
        user_id=conf.free_email_id,
        tariff=tariff,
        email=email.lower(),
        last_pay_id=pay_method
    )
    async with begin_connection () as conn:
        await conn.execute (query)


# выбирает пользователей для рассылки сообщения
async def get_users_for_message(group: str, start: datetime, end: datetime) -> [UserRow]:
    query = UserTable.select()
    if group == '0':
        query = query.where(sa.and_(
                UserTable.c.status == UserStatus.NEW.value,
                UserTable.c.first_visit > start,
                UserTable.c.first_visit <= end
        ))
    else:
        query = query.where(sa.and_(
                UserTable.c.status == UserStatus.NOT_SUB.value,
                UserTable.c.kick_date > start,
                UserTable.c.kick_date <= end
        ))

    async with begin_connection () as conn:
        result = await conn.execute (query)

    return result.all()
