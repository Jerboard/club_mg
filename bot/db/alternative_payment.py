import sqlalchemy as sa
import typing as t
from db.base import METADATA, begin_connection


class UserAlterPayMethodRow(t.Protocol):
    id: int
    orm_id: int
    name: str
    is_active: bool


UserAlterPayMethodTable = sa.Table(
    'alter_pay_method',
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('orm_id', sa.Integer),
    sa.Column('name', sa.String(255)),
    sa.Column('is_active', sa.Boolean),
)


# возвращает активные альтернативные способы оплаты
async def get_alter_pay_methods() -> tuple[UserAlterPayMethodRow]:
    query = UserAlterPayMethodTable.select ().where(UserAlterPayMethodTable.c.is_active == True)
    async with begin_connection () as conn:
        result = await conn.execute (query)
    return result.all ()


# возвращает активные альтернативные способы оплаты
async def get_alter_pay_method(method_id: int) -> UserAlterPayMethodRow:
    query = UserAlterPayMethodTable.select ().where (UserAlterPayMethodTable.c.id == method_id)
    async with begin_connection () as conn:
        result = await conn.execute (query)
    return result.first ()
