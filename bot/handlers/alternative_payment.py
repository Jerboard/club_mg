from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.enums.message_entity_type import MessageEntityType

import db
import keyboards as kb
from config import conf
from init import dp, bot
from utils.datetime_utils import add_months
from enums import UserCB, BaseStatus, UserStatus


# старт альтернативной оплаты
@dp.callback_query (lambda cb: cb.data.startswith(UserCB.SUPPORT_1.value))
async def support_1(cb: CallbackQuery, state: FSMContext):
    await state.set_state (BaseStatus.ALT_PAY_EMAIL)

    text = f'Отправьте мне сообщением адрес электронной почты, указанный при оплате'
    photo_id = await db.get_random_photo_id ()
    photo = InputMediaPhoto (media=photo_id.photo_id, caption=text)
    await cb.message.edit_media (photo, reply_markup=kb.back_start_button ())

    await state.update_data (data={'message_id': cb.message.message_id})


@dp.message (StateFilter(BaseStatus.ALT_PAY_EMAIL))
async def com_star_1t(msg: Message, state: FSMContext):
    data = await state.get_data ()
    if msg.entities and msg.entities[0].type == MessageEntityType.EMAIL.value:
        await state.clear ()
        user_info = await db.get_user_info(email=msg.text)
        if not user_info:
            text = 'Почта не найдена'

        elif user_info.user_id == conf.free_email_id:
            kick_date = add_months(count_months=int(user_info.tariff))
            await db.update_user_info(
                user_id=msg.from_user.id,
                email=msg.text,
                kick_date=kick_date,
                status=UserStatus.SUB.value,
                tariff=user_info.tariff,
                last_pay_id=user_info.last_pay_id
            )
            await bot.unban_chat_member (conf.channel_id, msg.from_user.id, only_if_banned=True)
            total_amount = await db.get_amount(user_info.tariff)
            await db.save_bill (user_id=msg.from_user.id, total_amount=total_amount, payment_id='on_email')

            text = f'✅ У вас оплачен период до {kick_date.strftime(conf.date_format)}\n\n' \
                   f'Для получения доступа и перехода в личный кабинет нажмите "🔙 На главный экран"'

            await db.delete_user_empty(user_info.id)

        elif user_info.user_id:
            text = 'Ваша почта уже зарегистрирована'

        else:
            text = 'Произошёл сбой обратитесь в поддержку'

    else:
        text = '❗️Некорректный адрес электронной почты'

    photo_id = await db.get_random_photo_id ()
    photo = InputMediaPhoto (media=photo_id.photo_id, caption=text)
    await bot.edit_message_media (
        chat_id=msg.chat.id,
        message_id=data ['message_id'],
        media=photo,
        reply_markup=kb.back_start_button ())
