import sqlalchemy as sa
import typing as t
from datetime import datetime

from db.base import METADATA, begin_connection
from config import conf


class PayYookassaTempRow(t.Protocol):
    id: int
    user_id: int
    pay_id: str
    status: str
    chat_id: str
    msg_id: str
    time: datetime
    tariff: int


PayYookassaTempTable = sa.Table(
    'pay_yookassa_temp',
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('user_id', sa.BigInteger),
    sa.Column('pay_id', sa.String(255)),
    sa.Column('status', sa.String(255)),
    sa.Column('chat_id', sa.BigInteger),
    sa.Column('msg_id', sa.Integer),
    sa.Column('time', sa.DateTime(timezone=True)),
    sa.Column('tariff', sa.Integer),
)


# сохраняет созданный платёж юкассы
async def save_pay_yoo(user_id: int, pay_id: str, chat_id: int, msg_id: int, tariff: int):
    now = datetime.now(conf.tz)
    query = PayYookassaTempTable.insert ().values (
        user_id=user_id,
        pay_id=pay_id,
        chat_id=chat_id,
        msg_id=msg_id,
        time=now,
        tariff=tariff
    )
    async with begin_connection () as conn:
        await conn.execute (query)


# возвращает настройки
async def get_pay_yoo(user_id: int, msg_id: int) -> PayYookassaTempRow:
    query = PayYookassaTempTable.select ().where (
        PayYookassaTempTable.c.user_id == user_id,
        PayYookassaTempTable.c.msg_id == msg_id,
    )
    async with begin_connection () as conn:
        result = await conn.execute (query)
    return result.first ()


# возвращает все записи юкассы
async def get_all_pay_yoo() -> tuple[PayYookassaTempRow]:
    query = PayYookassaTempTable.select ()
    async with begin_connection () as conn:
        result = await conn.execute (query)
    return result.all ()


# удаляет ожидающий платёж
async def del_from_yoo_temp(pay_id: int) -> None:
    query = PayYookassaTempTable.delete().where(PayYookassaTempTable.c.id == pay_id)

    async with begin_connection () as conn:
        await conn.execute (query)
