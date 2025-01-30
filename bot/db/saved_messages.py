import sqlalchemy as sa
import typing as t
from db.base import METADATA, begin_connection


class SaveMessagesRow(t.Protocol):
    id: int
    title: str
    text: str
    entities: list
    photo: str
    group_recip: str
    period_id: int


SaveMessagesTable = sa.Table(
    'save_messages',
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('title', sa.String(255)),
    sa.Column('text', sa.Text),
    sa.Column('entities', sa.ARRAY(sa.String)),
    sa.Column('photo', sa.String(255)),
    sa.Column('group_recip', sa.String(50)),
    sa.Column('period_id', sa.Integer),
)


# сохранить сообщение
async def save_message(title: str, text: str, entities: list, photo_id: str, group_recip: str, period_id: int) -> None:
    query = SaveMessagesTable.insert ().values (
        title=title,
        text=text,
        entities=entities,
        photo=photo_id,
        group_recip=group_recip,
        period_id=period_id,
    )
    async with begin_connection () as conn:
        await conn.execute (query)


# список сохранённых сообщений
async def get_all_save_messages() -> tuple[SaveMessagesRow]:
    query = SaveMessagesTable.select ()
    async with begin_connection () as conn:
        result = await conn.execute (query)
    return result.all ()


# список сохранённых сообщений сообщение
async def get_save_message(message_id: int) -> SaveMessagesRow:
    query = SaveMessagesTable.select ().where(SaveMessagesTable.c.id == message_id)
    async with begin_connection () as conn:
        result = await conn.execute (query)
    return result.first ()


# список сохранённых сообщений сообщение
async def del_save_messages(message_id: int) -> None:
    query = SaveMessagesTable.delete ().where (SaveMessagesTable.c.id == message_id)
    async with begin_connection () as conn:
        await conn.execute (query)
