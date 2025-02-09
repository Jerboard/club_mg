import sqlalchemy as sa
import typing as t
from db.base import METADATA, begin_connection


class AdminRow(t.Protocol):
    id: int
    user_id: str
    desc: str
    only_stat: bool


AdminTable = sa.Table(
    'admin',
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('user_id', sa.BigInteger, nullable=False),
    sa.Column('desc', sa.String(255)),
    sa.Column('only_stat', sa.Boolean),
)


# фильтр админ
async def admin_filter(user_id: int) -> bool:
    query = AdminTable.select().where(AdminTable.c.user_id == user_id)
    async with begin_connection() as conn:
        result = await conn.execute(query)

    if result.first():
        return True
    else:
        return False


# проверяет статус только статистика
# async def check_only_state(user_id: int) -> AdminRow:
async def get_admin_info(user_id: int) -> AdminRow:
    query = AdminTable.select().where(AdminTable.c.user_id == user_id)
    async with begin_connection() as conn:
        result = await conn.execute(query)
    return result.first()


# ид всех админов
async def get_admin_ids():
    query = AdminTable.select()
    async with begin_connection() as conn:
        result = await conn.execute(query)
    return result.all()


