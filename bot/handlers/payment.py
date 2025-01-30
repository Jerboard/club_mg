from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.enums.message_entity_type import MessageEntityType

from yookassa import Payment

import db
import keyboards as kb
from config import conf
from init import dp, bot, log_error
from enums import BaseStatus, UserCB


# запрос или подтверждение почты
@dp.callback_query (lambda cb: cb.data.startswith(UserCB.PAY_YOOKASSA_1.value))
async def com_start(cb: CallbackQuery, state: FSMContext):
    _, is_edit_str = cb.data.split (':')
    is_edit = bool(int(is_edit_str))

    user_info = await db.get_user_info (user_id=cb.from_user.id)
    photo_id = await db.get_random_photo_id ()

    if not user_info.email or is_edit:
        await state.set_state (BaseStatus.SEND_EMAIL)
        await state.update_data (data={'message_id': cb.message.message_id})

        if is_edit:
            text = f'Отправьте вашу новую электронную почту'
        else:
            text = '‼️Для регистрации в клубе отправьте вашу электронную почту.'

        photo = InputMediaPhoto (media=photo_id.photo_id, caption=text)
        await cb.message.edit_media (photo, reply_markup=kb.back_start_button())

    else:
        text = f'Ваша электронная почта: {user_info.email} ?'
        photo = InputMediaPhoto (media=photo_id.photo_id, caption=text)
        await cb.message.edit_media (media=photo, reply_markup=kb.accept_email ())


@dp.message (StateFilter(BaseStatus.SEND_EMAIL))
async def save_email(msg: Message, state: FSMContext):
    await msg.delete ()
    data = await state.get_data ()
    photo_id = await db.get_random_photo_id ()

    if msg.entities and msg.entities[0].type == MessageEntityType.EMAIL.value:
        await db.update_user_info(user_id=msg.from_user.id, email=msg.text)
        await state.clear ()

        text = f'<b>Выберете период подписки</b>'
        info = await db.get_info()
        keyboard = kb.select_tariff_kb (info)

    else:
        text = f'‼️Некорректный адрес электронной почты'
        keyboard = kb.back_start_button ()

    photo = InputMediaPhoto (media=photo_id.photo_id, caption=text)
    await bot.edit_message_media (
        chat_id=msg.from_user.id,
        message_id=data ['message_id'],
        media=photo,
        reply_markup=keyboard)


# оплата выбор тарифа
@dp.callback_query (lambda cb: cb.data.startswith(UserCB.PAY_YOOKASSA_0.value))
async def payment_1(cb: CallbackQuery):
    text = f'<b>Выберете период подписки</b>'
    photo_id = await db.get_random_photo_id()
    photo = InputMediaPhoto(media=photo_id.photo_id, caption=text)

    tariffs = await db.get_info()
    await cb.message.edit_media(photo, reply_markup=kb.select_tariff_kb(tariffs))


# оплата через юкассу
@dp.callback_query (lambda cb: cb.data.startswith(UserCB.PAY_YOOKASSA_2.value))
async def pay_yookassa_2(cb: CallbackQuery):
    _, count_mounts_str, amount_str = cb.data.split(':')
    count_mounts = int(count_mounts_str)
    amount = int(amount_str)
    user = await db.get_user_info(cb.from_user.id)

    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "bank_card"
        },
        'save_payment_method': True,
        "capture": True,
        "description": cb.from_user.id,
        "confirmation": {
            "type": "redirect",
            "return_url": conf.bot_link
        },
        "receipt": {
            "customer": {
                "email": user.email
            },
            "items": [
                {
                    "description": f"Образовательный проект Magirani CLUB {count_mounts} мес.",
                    "quantity": "1.00",
                    "amount": {
                        "value": amount,
                        "currency": "RUB"
                    },
                    "vat_code": "1",
                    "payment_mode": "full_payment",
                    "payment_subject": "service"
                }
            ]
        },
    })

    link = f'https://yoomoney.ru/api-pages/v2/payment-confirm/epl?orderId={payment.id}'

    text = 'Подтвердите выбранный период.\n\n' \
           '✔️После оплаты нажмите "Вернуться на сайт" ("Вернуться в магазин") и доступ будет сразу предоставлен.'
    photo_id = await db.get_random_photo_id()
    photo = InputMediaPhoto(media=photo_id.photo_id, caption=text, parse_mode='html')
    await cb.message.edit_media(photo, reply_markup=kb.pay_yookassa_kb(amount=amount, link=link))

    await db.save_pay_yoo(
        user_id=cb.from_user.id,
        pay_id=payment.id,
        chat_id=cb.message.chat.id,
        msg_id=cb.message.message_id,
        tariff=count_mounts)
