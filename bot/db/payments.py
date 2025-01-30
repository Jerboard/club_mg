import sqlalchemy as sa
import typing as t
from datetime import datetime

from db.base import METADATA, begin_connection
from config import conf


class PaymentRow(t.Protocol):
    id: int
    user_id: int
    date: datetime
    total_amount: int
    tg_payment_id: str
    provider_payment_charge_id: str


PaymentTable = sa.Table(
    'payments',
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('user_id', sa.BigInteger),
    sa.Column('date', sa.DateTime(timezone=True)),
    sa.Column('total_amount', sa.Integer),
    sa.Column('tg_payment_id', sa.String(100)),
    sa.Column('provider_payment_charge_id', sa.String(100)),
)


# сохраняет транзакцию
async def save_bill(user_id: int, total_amount: int, payment_id: str) -> None:
    query = PaymentTable.insert ().values(
        user_id=user_id,
        date=datetime.now(conf.tz).replace(microsecond=0),
        total_amount=total_amount,
        tg_payment_id=payment_id)
    async with begin_connection () as conn:
        await conn.execute (query)


# вся таблица пеймент
async def get_all_table_payments() -> tuple[PaymentRow]:
    query = PaymentTable.select ()
    async with begin_connection () as conn:
        result = await conn.execute (query)
    return result.all ()
