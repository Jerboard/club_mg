from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.enums.content_type import ContentType

from datetime import datetime, timedelta

import random
import logging

import db
from db.funnel import Funnel
import keyboards as kb
from config import conf
from init import dp, bot
from utils.message_utils import com_start_admin
from utils.entities_utils import save_entities, recover_entities
from utils.datetime_utils import minus_months
from data.base_data import periods
import utils as ut
from enums import AdminCB, BaseStatus, Action


# основная функция изменения сообщений
async def send_messages(state: FSMContext):
    await state.set_state(BaseStatus.SEND_USERS_MESSAGE)

    data = await state.get_data()
    await state.update_data(data={'save': False})
    #
    # print(f'--------')
    # for k, v in data.items():
    #     print(f'{k}: {v}')

    # for i in data['entities']:
    #     print(i)

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
            reply_markup=markup,
            parse_mode=None
        )

    else:
        if not data['edit_photo']:
            await bot.delete_message(chat_id=data['chat'], message_id=data['message'])
            sent = await bot.send_photo(
                chat_id=data['chat'],
                photo=data['photo'],
                caption=text,
                caption_entities=data['entities'],
                reply_markup=markup,
                parse_mode=None
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
        'save': False,
        'save_msg_id': None
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

    elif not data['text'] and not data['photo']:
        await cb.answer('❗️Нет сообщения для отправки', show_alert=True)

    else:

        # if user_period['unit'] == 'days':
        #     start = datetime.now(conf.tz) - timedelta(days=user_period['start'])
        #     end = datetime.now(conf.tz) - timedelta(days=user_period['end'])
        # else:
        #     start = minus_months(user_period['start'])
        #     end = minus_months(user_period['end'])
        #
        # if conf.debug:
        #     users = await db.get_all_users()
        # else:
        #     users = await db.get_users_for_message(group=data['group_recip'], start=start, end=end)

        user_period = periods[data['period_id']]
        users = await ut.get_milling_user_list(
            unit=user_period['unit'],
            group_recip=data['group_recip'],
            start=user_period['start'],
            end=user_period['end']
        )

        # users_ids = [user.user_id for user in users]
        # await state.update_data(data={'users_ids': users_ids})
        await cb.message.edit_reply_markup(reply_markup=None)
        text = (f'❕Пользователей получат сообщение {len(users)}\n'
                f'Подтвердить?')
        await cb.message.answer(text, reply_markup=kb.accept_send_message_kb())


# сохраняет сообщение
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.SEND_MESSAGES_6.value))
async def send_messages_6(cb: CallbackQuery, state: FSMContext):
    _, action = cb.data.split(':')
    data = await state.get_data()

    entities = save_entities(data['entities'])

    if not data['save']:
        icon = '🖼' if data['photo'] else ''
        date = datetime.now().strftime(conf.date_format)
        title_text = data['text'][:40] if data['text'] else 'Без текста'
        title = f'{icon} {date} {title_text}'.strip()

        if data.get('save_msg_id'):
            await db.update_message(
                msg_id=data['save_msg_id'],
                title=title,
                text=data['text'],
                entities=entities,
                photo_id=data['photo']
            )
            await state.update_data(data={'save': True})

        else:
            save_msg_id = await db.save_message(
                title=title,
                text=data['text'],
                entities=entities,
                photo_id=data['photo']
            )
            await state.update_data(data={'save': True, 'save_msg_id': save_msg_id})

    if action != Action.FUNNEL.value:
        await cb.answer('💾 Сохранено', show_alert=True)

    if action == Action.DEL.value:
        await state.clear()
        await cb.message.delete()
        await com_start_admin(cb.from_user.id)

    elif action == Action.FUNNEL.value:
        data = await state.get_data()

        if not data['group_recip']:
            await cb.answer('❗️Вы не выбрали группу пользователей', show_alert=True)

        elif not data['period_id']:
            await cb.answer('❗️Вы не выбрали период', show_alert=True)

        else:
            await state.clear()
            if data.get('funnel_id'):
                funnel_id = data['funnel_id']
            else:
                funnel_id = await Funnel.add(
                    user_id=cb.from_user.id,
                    save_msg_id=data.get('save_msg_id'),
                    group_recip=data['group_recip'],
                    period_id=data['period_id']
                )

            await ut.get_funnel_view(funnel_id=funnel_id, chat_id=cb.message.chat.id, msg_id=cb.message.message_id)


# отправить сообщение
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.SEND_MESSAGES_7.value))
async def send_messages_7(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    user_period = periods[data['period_id']]
    users = await ut.get_milling_user_list(
        unit=user_period['unit'],
        group_recip=data['group_recip'],
        start=user_period['start'],
        end=user_period['end']
    )

    await ut.mailing(
        chat_id=cb.message.chat.id,
        users=users,
        text=data['text'],
        entities_str=data['entities'],
        photo=data['photo'],
    )
    await bot.delete_message(chat_id=data['chat'], message_id=data['message'])


# удалить эскиз
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.SEND_MESSAGES_8.value))
async def send_messages_4(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.delete()
    await com_start_admin(cb.from_user.id)


# список сохранённых сообщений
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.SAVE_MESSAGES_1.value))
async def save_messages_1(cb: CallbackQuery, state: FSMContext):
    messages = await db.get_all_save_messages()

    if len(messages) == 0:
        await cb.answer('❗️У вас нет сохранённых сообщений', show_alert=True)
    else:
        await cb.message.edit_reply_markup(reply_markup=kb.get_save_message_kb(messages))


# обновить сохранённое сообщение
@dp.callback_query (lambda cb: cb.data.startswith(AdminCB.SAVE_MESSAGES_2.value))
async def save_messages_2(cb: CallbackQuery, state: FSMContext):
    _, save_message_id_str, funnel_id_str = cb.data.split(':')
    save_message_id = int(save_message_id_str)
    funnel_id = int(funnel_id_str)
    message = await db.get_save_message(save_message_id)
    funnel = await Funnel.get_by_id(funnel_id)

    entities = recover_entities (message.entities)

    await state.set_state('send_users_message')
    await state.update_data(data={
        'chat': cb.message.chat.id,
        'message': cb.message.message_id,
        'group_recip': funnel.group_recip if funnel else None,
        "period_id": funnel.period_id if funnel else None,
        'text': message.text,
        'entities': entities,
        'photo': message.photo,
        'edit': None,
        'edit_photo': None,
        'save': False,
        'save_msg_id': message.id,
        'funnel_id': funnel_id
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
