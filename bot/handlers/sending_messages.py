from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.enums.content_type import ContentType

from datetime import datetime, timedelta

import random
import logging

import db
import keyboards as kb
from config import conf
from init import dp, bot
from utils.message_utils import com_start_admin
from utils.entities_utils import save_entities, recover_entities
from utils.datetime_utils import minus_months
from data.base_data import periods
from enums import AdminCB, BaseStatus, UserStatus


# основная функция изменения сообщений
async def send_messages(state: FSMContext):
    await state.set_state(BaseStatus.SEND_USERS_MESSAGE)

    data = await state.get_data()
    await state.update_data(data={'save': False})
    #
    # print(f'--------')
    # for k, v in data.items():
    #     print(f'{k}: {v}')

    group_recip = data['group_recip']
    period_id = data['period_id']

    if data['text'] is None:
        text = 'Отправьте текст, картинку или картинку c подписью сообщением'
    else:
        text = data['text']

    markup = kb.get_send_message_kb(group_recip, period_id)

    if not data['photo']:
        await bot.edit_message_text(
            chat_id=data ['chat'],
            message_id=data ['message'],
            text=text,
            entities=data['entities'],
            reply_markup=markup)

    else:
        if not data['edit_photo']:
            await bot.delete_message(chat_id=data['chat'], message_id=data['message'])
            sent = await bot.send_photo(
                chat_id=data['chat'],
                photo=data['photo'],
                caption=text,
                caption_entities=data['entities'],
                reply_markup=markup
            )

            await state.update_data(data={'chat': sent.chat.id, 'message': sent.message_id, 'edit_photo': True})

        else:
            photo = InputMediaPhoto(media=data['photo'], caption=text)
            await bot.edit_message_media(
                chat_id=data ['chat'],
                message_id=data ['message'],
                media=photo,
                reply_markup=markup)


# вход в изменение сообщения
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.SEND_MESSAGES_1.value))
async def send_messages_1(cb: CallbackQuery, state: FSMContext):

    await state.set_state(BaseStatus.SEND_USERS_MESSAGE)
    await state.update_data(data={
        'chat': cb.message.chat.id,
        'message': cb.message.message_id,
        'group_recip': None,
        "period_id": None,
        'text': None,
        'entities': [],
        'photo': None,
        'edit': None,
        'edit_photo': None,
        'save': False
    })

    await send_messages(state)


# изменят выыбор группы пользователей
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.SEND_MESSAGES_2.value))
async def send_messages_2(cb: CallbackQuery, state: FSMContext):
    _, group_recip = cb.data.split(':')

    await state.update_data(data={'group_recip': group_recip})
    await send_messages(state)


# выводит подсказку
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.SEND_MESSAGES_3.value))
async def send_messages_3(cb: CallbackQuery, state: FSMContext):
    await cb.answer('Выберите период')


# изменят выбор периода
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.SEND_MESSAGES_4.value))
async def send_messages_4(cb: CallbackQuery, state: FSMContext):
    _, period_id_str = cb.data.split(':')
    period_id = int(period_id_str)

    data = await state.get_data()
    if data['period_id'] == period_id:
        period_id = None

    await state.update_data(data={'period_id': period_id})
    await send_messages(state)


@dp.message(StateFilter(BaseStatus.SEND_USERS_MESSAGE))
async def send_users_message(msg: Message, state: FSMContext):
    await msg.delete()
    entities = msg.entities if msg.entities else msg.caption_entities
    if msg.content_type == ContentType.TEXT:
        await state.update_data(data={'text': msg.text, 'edit': 'text', 'entities': entities})
    else:
        if msg.caption:
            await state.update_data(data={
                'photo': msg.photo[-1].file_id,
                'text': msg.caption,
                'entities': entities,
                'edit': 'media'
            })
        else:
            await state.update_data(data={'photo': msg.photo[-1].file_id, 'edit': 'media'})

        data = await state.get_data()
        if data['edit_photo'] is None:
            await state.update_data(data={'edit_photo': False})

        elif not data['edit_photo']:
            await state.update_data(data={'edit_photo': True})

    await send_messages(state)


# проверить перед отправкой тут сохраняется группа пользователей
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.SEND_MESSAGES_5.value))
async def send_messages_4(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if not data['group_recip']:
        await cb.answer('❗️Вы не выбрали группу пользователей', show_alert=True)

    elif not data['period_id']:
        await cb.answer('❗️Вы не выбрали период', show_alert=True)

    elif not data['text']:
        await cb.answer('❗️Нет сообщения для отправки', show_alert=True)

    else:
        user_period = periods[data['period_id']]

        if user_period['unit'] == 'days':
            start = datetime.now(conf.tz) - timedelta(days=user_period['start'])
            end = datetime.now(conf.tz) - timedelta(days=user_period['end'])
        else:
            start = minus_months(user_period['start'])
            end = minus_months(user_period['end'])

        users = await db.get_users_for_message(group=data['group_recip'], start=start, end=end)
        users_ids = [user.user_id for user in users]
        await state.update_data(data={'users_ids': users_ids})
        await cb.message.edit_reply_markup(reply_markup=None)
        text = f'❕Пользователей получат сообщение {len(users)}\n' \
               f'Подтвердить?'
        await cb.message.answer(text, reply_markup=kb.accept_send_message_kb())


# сохраняет сообщение
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.SEND_MESSAGES_6.value))
async def send_messages_6(cb: CallbackQuery, state: FSMContext):
    _, del_message_str = cb.data.split(':')
    del_message = bool(int(del_message_str))
    data = await state.get_data()

    entities = save_entities(data['entities'])

    if not data['save']:
        title = data['text'][:40]
        await db.save_message(
            title=title,
            text=data['text'],
            entities=entities,
            photo_id=data['photo'],
            group_recip=data['group_recip'],
            period_id=data['period_id']
        )
        await state.update_data(data={'save': True})

    await cb.answer('💾 Сохранено')

    if del_message:
        await state.clear()
        await cb.message.delete()
        await com_start_admin(cb.from_user.id)


# отправить сообщение
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.SEND_MESSAGES_7.value))
async def send_messages_7(cb: CallbackQuery, state: FSMContext):
    time_start = datetime.now()
    data = await state.get_data()
    await state.clear()
    users_ids: list = data.get('users_ids', [])

    counter = 0
    sent = await cb.message.answer(f'⏳ Отправлено {counter}/{len(users_ids)}')

    for user_id in users_ids:
        try:
            if not data.get('photo'):
                await bot.send_message(chat_id=user_id, text=data['text'], reply_markup=kb.del_message_user())

            else:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=data['photo'],
                    caption=data['text'],
                    reply_markup=kb.del_message_user())
            counter += 1
            # if counter % 100 == 0:
            if random.randint(1, 50) == 1:
                await sent.edit_text(f'⏳ Отправлено {counter}/{len(users_ids)}')

        except Exception as ex:
            pass

    await bot.delete_message(chat_id=data['chat'], message_id=data['message'])

    text = f'✅ {counter} из {len(users_ids)} сообщений успешно отправлено'
    await sent.edit_text(text)
    logging.warning(f'Отправил {counter} сообщений за: {datetime.now () - time_start}')
    # await cb.message.edit_text(text, reply_markup=kb.back_admin_menu_kb())


# удалить эскиз
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.SEND_MESSAGES_8.value))
async def send_messages_4(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.delete()
    await com_start_admin(cb.from_user.id)


# список сохранённых сообщений
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.SAVE_MESSAGES_1.value))
async def send_messages_4(cb: CallbackQuery, state: FSMContext):
    messages = await db.get_all_save_messages()

    if len(messages) == 0:
        await cb.answer('❗️У вас нет сохранённых сообщений', show_alert=True)
    else:
        await cb.message.edit_reply_markup(reply_markup=kb.get_save_message_kb(messages))


# обновить сохранённое сообщение
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.SAVE_MESSAGES_2.value))
async def send_messages_4(cb: CallbackQuery, state: FSMContext):
    _, save_message_id_str = cb.data.split(':')
    save_message_id = int(save_message_id_str)
    message = await db.get_save_message(save_message_id)

    entities = recover_entities (message.entities)

    await state.set_state('send_users_message')
    await state.update_data(data={
        'chat': cb.message.chat.id,
        'message': cb.message.message_id,
        'group_recip': message.group_recip,
        "period_id": message.period_id,
        'text': message.text,
        'entities': entities,
        'photo': message.photo,
        'edit': None,
        'edit_photo': None,
        'save': False
    })

    await send_messages(state)


# удалить сообщение у пользователя
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.DEL_MESSAGE_1.value))
async def del_message_1(cb: CallbackQuery, state: FSMContext):
    _, save_message_id_str = cb.data.split (':')
    save_message_id = int (save_message_id_str)

    await db.del_save_messages(save_message_id)
    messages = await db.get_all_save_messages()

    if len(messages) == 0:
        await cb.answer('❗️У вас нет сохранённых сообщений')
        admin = await db.get_admin_info(cb.from_user.id)
        await cb.message.edit_reply_markup(reply_markup=kb.get_first_admin_kb(admin.only_stat))
    else:
        await cb.message.edit_reply_markup(reply_markup=kb.get_save_message_kb(messages))
