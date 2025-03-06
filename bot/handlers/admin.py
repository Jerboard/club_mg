from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.enums.message_entity_type import MessageEntityType

import logging
import asyncio

from datetime import datetime

import db
import keyboards as kb
from config import conf
from init import dp, bot
from utils.datetime_utils import add_months
from utils.message_utils import com_start_admin
from enums import AdminCB, BaseStatus, UserStatus


# админка
@dp.message (StateFilter(default_state))
async def admin(msg: Message, state: FSMContext):
    await msg.delete ()
    admin_info = await db.get_admin_info (msg.from_user.id)
    if not admin_info:
        return

    if msg.entities and msg.entities[0].type == MessageEntityType.EMAIL.value:
        email = msg.text.lower()
        user_info = await db.get_user_info (email=email)

        await state.set_state (BaseStatus.ADD_USER_EMAIL)
        await state.update_data (data={
            'email': email,
            'user_id': user_info.user_id if user_info else None
        })

        if user_info:
            if user_info.user_id == 11111:
                text = 'Для продления доступа пользователю необходимо получить доступ по текущему тарифу.'
                await msg.answer (text)

            else:
                username = f'Юзернейм: {user_info.username}\n' if user_info.username is not None else ""
                kick_date = user_info.kick_date.strftime (conf.date_format) if user_info.kick_date is not None else 'Нет даты'
                text = f'❗Пользователь уже существует\n' \
                       f'Имя: {user_info.full_name}\n' \
                       f'{username}' \
                       f'Дата кика: {kick_date}\n' \
                       f'Рекуррент: {bool (user_info.recurrent)}\n' \
                       f'Тариф: {user_info.tariff} мес.\n' \
                       f'Почта: {user_info.email}\n\n' \
                       f'Добавить?'

                methods = await db.get_alter_pay_methods()
                await msg.answer (text, reply_markup=kb.get_alter_pay_methods_kb (methods))

        else:
            methods = await db.get_alter_pay_methods ()
            await msg.answer (f'Почта: {msg.text}', reply_markup=kb.get_alter_pay_methods_kb (methods))

    else:
        await msg.answer (f'Некорректный email: {msg.text}')


# добавляет пользователя
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.ADD_MONTHS_1.value))
async def add_months_1(cb: CallbackQuery, state: FSMContext):
    _, method_id_str = cb.data.split (':')
    method_id = int(method_id_str)
    await state.update_data (data={'method_id': method_id})
    await cb.message.edit_reply_markup (reply_markup=kb.get_add_months_kb ())


# добавляет пользователя
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.ADD_MONTHS_2.value))
async def add_months_2(cb: CallbackQuery, state: FSMContext):
    _, tariff_str = cb.data.split (':')
    data = await state.get_data ()
    await state.clear ()
    # logging.warning(f'tariff_str>>>>> : {tariff_str}')
    # logging.warning(f'data>>>>> : {data}')

    if tariff_str == 'del':
        await cb.message.delete ()

    else:
        tariff = int(tariff_str)
        if not data.get('user_id'):
            pay_method = await db.get_alter_pay_method (method_id=data ['method_id'])
            await db.add_email_wo_user (email=data ['email'], tariff=tariff_str, pay_method=pay_method.name)
            await cb.message.edit_text (f'✅Почта добавлена {data ["email"]}')

        else:
            user_info = await db.get_user_info(user_id=data ['user_id'])
            pay_method = await db.get_alter_pay_method (method_id=data ['method_id'])

            kick_date = add_months(kick_date=user_info.kick_date, count_months=tariff)
            await db.update_user_info(
                user_id=data ['user_id'],
                kick_date=kick_date,
                status=UserStatus.SUB.value,
                tariff=tariff_str,
                last_pay_id=pay_method.name
            )

            total_amount = await db.get_amount(tariff)
            await db.save_bill (user_id=user_info.user_id, total_amount=total_amount, payment_id=pay_method.name)
            await bot.unban_chat_member (
                chat_id=conf.channel_id,
                user_id=user_info.user_id,
                only_if_banned=True
            )

            await cb.message.edit_text (f'✅Продлено {data ["email"]} до {kick_date.strftime (conf.date_format)}')
            try:
                text = f'✅ Ваш доступ успешно продлён до {kick_date.strftime (conf.date_format)}.' \
                       f'Для продолжения нажмите "🔙 На главный экран"👇'

                photo_id = await db.get_random_photo_id ()
                await bot.send_photo (chat_id=data ['user_id'],
                                      photo=photo_id.photo_id,
                                      caption=text,
                                      reply_markup=kb.back_start_button())
            except Exception as ex:
                logging.warning (f'admin 112 {ex}')
                await db.reg_action (
                    user_id=data ['user_id'],
                    status='failed',
                    action='Сообщение о продлении по емейлу',
                    comment='Сообщение не отправлено')
                await cb.message.answer ('Сообщение не отправлено')


# возвращает к старту для админа
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.BACK_ADMIN_START.value))
async def back_admin(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.delete()
    await com_start_admin(cb.from_user.id)


# удалить пользователя
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.DEL_USER_1.value))
async def del_user_1(cb: CallbackQuery, state: FSMContext):
    await state.set_state(BaseStatus.DEL_USER)

    await cb.message.edit_text('<b>Отправьте ID пользователя или email</b>', reply_markup=kb.back_admin_menu_kb(True))


@dp.message(StateFilter(BaseStatus.DEL_USER))
async def del_user_2(msg: Message):
    await msg.delete()
    if msg.text.isdigit():
        user = await db.get_user_info(user_id=int(msg.text))
    else:
        user = await db.get_user_info (email=msg.text)

    if not user:
        sent = await msg.answer(f'❌Пользователь {msg.text} не найден', reply_markup=kb.get_close_kb())
        await asyncio.sleep(3)
        await sent.delete()

    else:
        await bot.ban_chat_member(conf.channel_id, user_id=user.user_id)
        await db.update_user_info(
            user_id=user.user_id,
            recurrent=False,
            status=UserStatus.REFUND.value,
            kick_date=datetime.now(conf.tz).date()
        )
        text = f'Пользователь {user.full_name} удалён'
        sent = await msg.answer(text)
        await asyncio.sleep(3)
        await sent.delete()
