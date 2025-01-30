from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from aiogram.fsm.context import FSMContext

import db
import keyboards as kb
from init import dp
from utils.message_utils import get_start_screen_for_user
from utils.statistic_utils import get_statistic_text
from enums import BaseCB, UserCB


# старт
@dp.message (CommandStart())
async def com_start(msg: Message, state: FSMContext):
    await state.clear ()
    admin_info = await db.get_admin_info(msg.from_user.id)
    if admin_info:
        text = await get_statistic_text()
        await msg.answer(text=text, reply_markup=kb.get_first_admin_kb(admin_info.only_stat))

    else:
        await get_start_screen_for_user(
            user_id=msg.from_user.id,
            full_name=msg.from_user.full_name,
            username=msg.from_user.username
        )


@dp.callback_query (lambda cb: cb.data.startswith(BaseCB.BACK_COM_START.value))
async def back_com_start(cb: CallbackQuery, state: FSMContext):
    await state.clear ()

    await get_start_screen_for_user (
        user_id=cb.from_user.id,
        content_type=cb.message.content_type,
        full_name=cb.from_user.full_name,
        username=cb.from_user.username,
        message_id=cb.message.message_id
    )


# # смена кб на техподдержку
@dp.callback_query (lambda cb: cb.data.startswith(UserCB.SUPPORT_0.value))
async def support_kb(cb: CallbackQuery):
    text = f'<b>Для получения доступа после оплаты альтернативным способом нажмите "Доступ по EMAIL"</b>\n\n' \
           f'Чтобы задать вопрос, нажмите "Написать в техподдержку"'

    photo_id = await db.get_random_photo_id ()
    photo = InputMediaPhoto (media=photo_id.photo_id, caption=text)
    await cb.message.edit_media (photo, reply_markup=kb.get_support_kb ())


# отмена
@dp.callback_query (lambda cb: cb.data.startswith(BaseCB.CLOSE.value))
async def close(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.delete()
