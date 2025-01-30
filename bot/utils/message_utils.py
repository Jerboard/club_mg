from aiogram.types import InputMediaPhoto
from aiogram.enums.content_type import ContentType
from aiogram.exceptions import TelegramBadRequest
from datetime import datetime, date

import db
import keyboards as kb
from config import conf
from init import bot, log_error
from utils.statistic_utils import get_statistic_text
from enums import UserStatus


# текс приветствия
def get_hello_text(text_number: int, user_kick_date: date) -> str:
    data_str = user_kick_date.strftime(conf.date_format)
    if text_number == 1:
        text = f'Ты здесь и это значит, что целительное поле УЖЕ работает! ' \
               f'<b>Сама энергия жизни ведёт тебя в правильное место...💜</b>\n\n' \
               f'Чтобы присоединиться к клубу нажмите "Перейти к оплате", ' \
               f'чтобы войти в поле Магирани <i><b>прямо сейчас</b></i>.'

    elif text_number == 2:
        text = f'Рада снова вас видеть 🌿🔮\n\n' \
               f'<b>Период вашей подписки в MAGIRANI CLUB закончился.</b>\n\n' \
               f'Чтобы продлить подписку и быть в поле Магирани, нажмите "Перейти к оплате"👇'

    elif text_number == 3:
        text = f'<b>✨ У вас оплачен период до {data_str}</b>\n\n' \
               f'Продление произойдёт автоматически.\n\n' \
               f'Чтобы получить доступ нажмите "Личный кабинет" и "Перейти в канал".\n' \
               f'Отказаться от подписки вы сможете в "Личном кабинете"'
    else:
        text = f'<b>✨ У вас оплачен период до {data_str}</b>\n\n' \
               f'Для получения доступа нажмите перейти в канал👇\n\n' \
               f'Для продления нажмите кнопку "Перейти к оплате" или ' \
               f'напишите в техподдержку для оплаты альтернативным способом.'

    return text


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
