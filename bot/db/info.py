import sqlalchemy as sa
import typing as t
from db.base import METADATA, begin_connection


class InfoRow(t.Protocol):
    id: int
    cost_1: int
    cost_3: int
    cost_6: int
    cost_12: int


InfoTable = sa.Table(
    'info',
    METADATA,
    sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column('cost_1', sa.Integer),
    sa.Column('cost_3', sa.Integer),
    sa.Column('cost_6', sa.Integer),
    sa.Column('cost_12', sa.Integer),
)


# возвращает настройки
async def get_info() -> InfoRow:
    query = InfoTable.select ()
    async with begin_connection () as conn:
        result = await conn.execute (query)
    return result.first ()


async def get_amount(tariff):
    tariff = int(tariff)
    info = await get_info()
    if tariff == 1:
        total_amount = info.cost_1
    elif tariff == 3:
        total_amount = info.cost_3
    elif tariff == 6:
        total_amount = info.cost_6
    elif tariff == 12:
        total_amount = info.cost_12
    else:
        total_amount = 0
    return int(total_amount)
