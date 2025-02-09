import sqlalchemy as sa
import typing as t
from db.base import METADATA, begin_connection


class SaveMessagesRow(t.Protocol):
    id: int
    title: str
    text: str
    entities: str
    photo: str
    # group_recip: str
    # period_id: int


SaveMessagesTable = sa.Table(
    'save_messages',
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('title', sa.String(255)),
    sa.Column('text', sa.Text),
    # sa.Column('entities', sa.ARRAY(sa.String)),
    sa.Column('entities', sa.Text),
    sa.Column('photo', sa.String(255)),
)


# сохранить сообщение
async def save_message(title: str, text: str, entities: str, photo_id: str) -> int:
    query = SaveMessagesTable.insert ().values (
        title=title,
        text=text,
        entities=entities,
        photo=photo_id,
    )
    async with begin_connection () as conn:
        result = await conn.execute (query)

    return result.inserted_primary_key[0]


# сохранить сообщение
async def update_message(
        msg_id: int,
        title: str = None,
        text: str = None,
        entities: str = None,
        photo_id: str = None
) -> None:
    query = SaveMessagesTable.update ().where(SaveMessagesTable.c.id == msg_id)

    if title:
        query = query.values (title=title)
    if text:
        query = query.values (text=text)
    if entities:
        query = query.values (entities=entities)
    if photo_id:
        query = query.values (photo=photo_id)

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
