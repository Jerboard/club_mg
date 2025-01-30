import sqlalchemy as sa
import typing as t

from db.base import METADATA, begin_connection
from config import conf


class PhotosRow(t.Protocol):
    id: int
    photo_id: str


PhotosTable = sa.Table(
    'photos',
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('photo_id', sa.String(100)),
)


# фото для теста бот https://t.me/tushchkan_test_3_bot
class PhotosRowTest:
    def __init__(self):
        self.photo_id = 'AgACAgIAAxkBAAM4ZflLbJApUlsBy5eZ_iRm2cOWaEYAAsXUMRtsrslLIQx4uxnCLwwBAAMCAAN5AAM0BA'


async def add_photo_pull(photo_id: str) -> None:
    query = PhotosTable.insert ().values (photo_id=photo_id)
    async with begin_connection () as conn:
        await conn.execute (query)


# даёт ид рандомной фотки
async def get_random_photo_id() -> PhotosRow:
    query = PhotosTable.select ().order_by(sa.func.random())
    async with begin_connection () as conn:
        result = await conn.execute (query)
    if conf.debug:
        return PhotosRowTest()
    else:
        return result.first ()
