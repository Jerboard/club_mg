from aiogram.types import InputMediaPhoto
from aiogram.enums.content_type import ContentType
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

import random

import db
from db.funnel import Funnel
from db.mailing_journal import MailJournal
import keyboards as kb
from config import conf
from init import bot, log_error
from .statistic_utils import get_statistic_text
from .text_utils import get_hello_text
from .datetime_utils import get_next_start_date
from .entities_utils import recover_entities
from enums import UserStatus, Unit


# главный экран пользователя
async def get_start_screen_for_user(
        user_id: int,
        content_type: str = ContentType.TEXT.value,
        full_name: str = None,
        username: str = None,
        message_id: int = None
) -> None:
    user_info = await db.get_user_info (user_id=user_id)

    if user_info and user_info.status == UserStatus.BAN.value:
        text = ('Здравствуйте, к сожалению не смогу с вами взаимодействовать. '
                'Что-то пошло не так, напишите пожалуйста в поддержку.')
        await bot.send_message (user_id, text, reply_markup=kb.get_ban_kb())
        return

    text_number = 1
    keyboard_type = 0
    if not user_info:
        await db.add_user (
            user_id=user_id,
            full_name=full_name,
            username=username)

    elif user_info.status == UserStatus.NOT_SUB.value:
        text_number = 2

    elif user_info.status == UserStatus.SUB.value and user_info.recurrent:
        text_number = 3
        keyboard_type = 1

    elif user_info.status == UserStatus.SUB.value and not user_info.recurrent:
        text_number = 4
        keyboard_type = 2

    if user_info and user_info.kick_date:
        user_kick_date = user_info.kick_date
    else:
        user_kick_date = datetime.now (conf.tz).date ()

    if user_info:
        if not full_name:
            full_name = user_info.full_name
        if not username:
            username = user_info.username

        if full_name != user_info.full_name or username != user_info.username:
            try:
                await db.update_user_info (
                    user_id=user_id,
                    full_name=full_name,
                    username=username
                )
            except Exception as ex:
                log_error(f'user_id: {user_id}\nfull_name: {full_name}\nusername: {username}\n',
                          with_traceback=False)
                log_error(ex)

    text = get_hello_text (text_number=text_number, user_kick_date=user_kick_date)

    photo_id = await db.get_random_photo_id ()

    try:
        if content_type == ContentType.TEXT.value:
            if message_id:
                await bot.delete_message(chat_id=user_id, message_id=message_id)

            await bot.send_photo (
                chat_id=user_id,
                photo=photo_id.photo_id,
                caption=text,
                reply_markup=kb.com_start_kb (keyboard_type))
        else:
            photo = InputMediaPhoto (media=photo_id.photo_id, caption=text)
            await bot.edit_message_media (
                chat_id=user_id,
                message_id=message_id,
                media=photo,
                reply_markup=kb.com_start_kb (keyboard_type))
    except TelegramBadRequest as ex:
        log_error(ex, with_traceback=False)

    await db.reg_action(
        user_id=user_id,
        status='successfully',
        action='Нажал "Старт"'
    )


# отправить сообщение всем админам
async def send_message_admins(text):
    admins = await db.get_admin_ids ()
    for admin in admins:
        await bot.send_message (admin [0], text)


# админ меню
async def com_start_admin(user_id):
    text = await get_statistic_text()
    admin = await db.get_admin_info(user_id)
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb.get_first_admin_kb(admin.only_stat))


# возвращает список пользовтаелей
async def get_milling_user_list(unit: str, group_recip: str, start: int, end: int, ) -> list[db.UserRow]:
    now = datetime.now(conf.tz)
    if unit == Unit.DAYS.value:
        start = now - timedelta(days=start)
        end = now - timedelta(days=end)
    else:
        start = now - relativedelta(months=start)
        end = now - relativedelta(months=end)

    users = await db.get_users_for_message(group=group_recip, start=start, end=end)
    return users


# рассылает сообщение
async def mailing(
        chat_id: int,
        users: list[db.UserRow],
        text: str = None,
        entities_str: str = None,
        photo: str = None,
):
    start_time = datetime.now()
    counter = 0
    sent = await bot.send_message(chat_id=chat_id, text=f'⏳ Отправлено {counter}/{len(users)}')
    entities = recover_entities(entities_str)

    blocked, unblocked = 0, 0

    for user in users:
        try:
            if not photo:
                await bot.send_message(
                    chat_id=user.user_id,
                    text=text,
                    entities=entities,
                    parse_mode=None,
                    reply_markup=kb.del_message_user()
                )

            else:
                await bot.send_photo(
                    chat_id=user.user_id,
                    photo=photo,
                    caption=text,
                    caption_entities=entities,
                    parse_mode=None,
                    reply_markup=kb.del_message_user())
            counter += 1

            if user.is_blocked:
                await db.update_user_info(user_id=user.user_id, is_blocked=False)
                unblocked += 1

            if random.randint(1, 50) == 1:
                await sent.edit_text(f'⏳ Отправлено {counter}/{len(users)}')

        except TelegramForbiddenError as ex:
            if not user.is_blocked:
                await db.update_user_info(user_id=user.user_id, is_blocked=True)
                blocked += 1

        except Exception as ex:
            log_error(ex)

    mailing_time = datetime.now() - start_time
    text = (
        f'✅ {counter} из {len(users)} сообщений успешно отправлено за {mailing_time}\n'
        f'Заблокировали бот: {blocked}\n'
        f'Разблокировали бот: {unblocked}'
        )
    await sent.edit_text(text)

    await MailJournal.add(
        all_msg=len(users),
        success=counter,
        failed=len(users) - counter,
        blocked=blocked,
        unblocked=unblocked,
        time_mailing=mailing_time,
        report=text
    )


# показывает воронку
async def get_funnel_view(funnel_id: int, chat_id: int, msg_id: int = None):
    funnel = await Funnel.get_by_id(funnel_id)
    entities = recover_entities(funnel.entities)

    next_start = get_next_start_date(next_start_date=funnel.next_start_date, next_start_time=funnel.next_start_time)
    next_start_str = next_start.strftime(conf.datetime_format)

    text = f'{funnel.text}\n-----\nВремя следующей рассылки: {next_start_str}'.replace('None', '')

    if msg_id:
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)

    if funnel.photo:
        await bot.send_photo(
            chat_id=chat_id,
            photo=funnel.photo,
            caption=text,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=kb.get_funnel_edit_kb(funnel)
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            entities=entities,
            parse_mode=None,
            reply_markup=kb.get_funnel_edit_kb(funnel)
        )
