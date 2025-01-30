from aiogram.types import CallbackQuery, InputMediaPhoto

import db
import keyboards as kb
from init import dp
from utils.message_utils import get_start_screen_for_user
from enums import UserCB


# # личный кабинет
@dp.callback_query (lambda cb: cb.data.startswith(UserCB.MY_ACCOUNT.value))
async def com_start(cb: CallbackQuery):
    text = f'Чтобы отказаться от автоматического продления нажмите кнопку "Отказаться от подписки"'
    photo_id = await db.get_random_photo_id ()
    photo = InputMediaPhoto (media=photo_id.photo_id, caption=text)
    await cb.message.edit_media (photo, reply_markup=kb.get_unsubscribe_kb ())


# отменяет реккурент отправляет на главный экран
@dp.callback_query (lambda cb: cb.data.startswith(UserCB.UNSUBSCRIBE.value))
async def com_start(cb: CallbackQuery, ):
    await db.update_user_info(user_id=cb.from_user.id, recurrent=False)

    await cb.answer ('❗️Автоматическое продление подписки отключено', show_alert=True)
    await get_start_screen_for_user(
        user_id=cb.from_user.id,
        message_id=cb.message.message_id,
        content_type=cb.message.content_type
    )
