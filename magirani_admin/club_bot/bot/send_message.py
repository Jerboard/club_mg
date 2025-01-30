from telebot.types import InputMediaPhoto
from datetime import date

import club_bot.bot.keyboards as kb
from club_bot.bot import db
from club_bot.bot.base import bot, log_error
from club_bot.enums import UserStatus, RecurrentStatus
from magirani_admin.settings import DATE_FORMAT, CHANNEL_ID


def send_message_admin(text: str):
    try:
        bot.send_message(chat_id=524275902, text=text, disable_notification=True)
    except Exception as ex:
        log_error(ex)


# подтверждает успешную оплату
def success_payment(user_id: int, message_id: int, new_kick_date: date, user_status: str, photo_id: str = None):
    text = (f'✅ Оплата прошла успешно, подписка продлена до {new_kick_date.strftime (conf.date_format)}\n\n'
            f'Нажмите кнопку "🔙 На главный экран" ')

    if user_status == UserStatus.SUB.value:
        try:
            bot.edit_message_caption (
                chat_id=user_id,
                message_id=message_id,
                caption=text,
                reply_markup=kb.get_back_start_kb())

        except Exception as ex:
            print(ex)
            log_error (ex)

    else:
        #  исправить link.invite_link
        # unban = bot.unban_chat_member (chat_id=CHANNEL_ID, user_id=user_id, only_if_banned=True)
        # if unban:
        #     db.reg_action (user_id=user_id, status='successfully', action='разбан')
        #
        # link = bot.create_chat_invite_link (conf.channel_id, member_limit=1)
        link = 'https://t.me/tushchkan_test_3_bot'
        db.reg_action (
            user_id=user_id,
            status='successfully',
            action='создана ссылка',
            comment=link
        )

        try:
            # photo = InputMediaPhoto (media=photo_id, caption=text)
            # print(text)
            bot.edit_message_caption (
                caption=text,
                chat_id=user_id,
                message_id=message_id,
                reply_markup=kb.get_succeeded_link_kb (link)
            )
        except Exception as ex:
            log_error (ex)
            db.reg_action (
                user_id=user_id,
                status='failed',
                action='Сообщение подтверждения оплаты не изменено',
                comment=f'ex: {ex}'
            )


# предупреждение о конце рекуррента или о недостатке сретств
def send_info_message(user_id: int, text: str):
    try:
        bot.send_message(chat_id=user_id, text=text, reply_markup=kb.get_back_start_kb())
        db.reg_action (
            user_id=user_id,
            status='successfully',
            action='Сообщение подтверждения оплаты не изменено'
        )
    except Exception as ex:
        db.reg_action (
            user_id=user_id,
            status='failed',
            action='Предупреждение',
            comment=f'ex: {ex}'
        )
