import asyncio
import logging
from yookassa import Payment
from aiogram.types import InputMediaPhoto

from datetime import timedelta, datetime

import db
import keyboards as kb
from config import conf
from init import bot, log_error
from utils.users_utils import ban_user
from utils.datetime_utils import add_months
from .redis_utils import set_start_recurrent, is_start_recurrent_set
from enums import UserStatus


# проверка подписки автоплатежа
async def check_sub():
    log_error('>>>>>>>>>>>>>>>>>>>>>. check_sub', with_traceback=False)
    # проверяем запускался ли реккурент
    if is_start_recurrent_set() or conf.debug:
        return False

    # записываем запуск реккурента
    set_start_recurrent()

    today = datetime.now(conf.tz).date()
    next_kick_data = today + timedelta(days=2)
    users = await db.get_all_users(status=UserStatus.SUB.value, target_date=next_kick_data)
    for user in users:
        try:
            if user.recurrent:
                if user.kick_date <= today:
                    # amount = await db.get_amount(user.tariff)
                    amount = await db.get_amount('1')

                    payment = Payment.create({
                        "amount": {
                            "value": amount,
                            "currency": "RUB"
                        },
                        'save_payment_method': True,
                        "capture": True,
                        "payment_method_id": user.last_pay_id,
                        "description": user.user_id,
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
                                    "description": f"Magirani CLUB {user.tariff} мес.",
                                    "quantity": "1.00",
                                    "amount": {
                                        "value": amount,
                                        "currency": "RUB"
                                    },
                                    "vat_code": "1",
                                    "payment_mode": "full_payment",
                                    "pament_subject": "service"
                                }
                            ]
                        },
                    })

                    pay_stat = payment.paid
                    if payment.paid:
                        new_kick_date = add_months(count_months=int(user.tariff), kick_date=user.kick_date)
                        await db.update_user_info(
                            user_id=user.user_id,
                            kick_date=new_kick_date,
                            status=UserStatus.SUB.value,
                            last_pay_id=payment.id,
                            tariff='1'
                        )

                        await db.save_bill(user_id=user.user_id, total_amount=amount, payment_id=payment.id)
                        await db.reg_action (user_id=user.user_id, status='successfully', action='снятие рекуррента')
                    else:
                        await db.reg_action (
                            user_id=user.user_id,
                            status='failed',
                            action='снятие рекуррента',
                            comment=f'pay_status: {pay_stat}')

                        await ban_user(user_id=user.user_id)

                else:
                    pass

            else:
                if user.kick_date <= today:
                    try:
                        await ban_user(user.user_id)
                    except Exception as ex:
                        log_error (ex)
                        await db.reg_action (
                            user_id=user.user_id,
                            status='failed',
                            action='бан конец подписки',
                            comment=str(ex))

                else:
                    if not user.alarm_2_day:
                        text = (f'Ваша подписка на канал {conf.channel_name} заканчивается через 2 дня, чтобы '
                                f'продлить подписку нажмите /start и продлите подписку.')
                        try:
                            photo_id = await db.get_random_photo_id()
                            await bot.send_photo(chat_id=user.user_id, caption=text, photo=photo_id.photo_id)

                            await db.update_user_info (user_id=user.user_id, alarm_2_day=True)
                            await db.reg_action (
                                user_id=user.user_id,
                                status='successfully',
                                action='предупреждение о конце срока подписки',
                                comment=f'Кик дата: {user.kick_date.strftime(conf.date_format)}'
                            )
                        except Exception as ex:
                            await db.reg_action (
                                user_id=user.user_id,
                                status='failed',
                                action='предупреждение о конце срока подписки',
                                comment=f'{ex}\nКик дата: {user.kick_date.strftime (conf.date_format)}'
                            )
                    else:
                        pass

            await asyncio.sleep(3)
        except Exception as ex:
            log_error(ex)
            await db.reg_action (
                user_id=user.user_id,
                status='failed',
                action=f'ВОТ ЭТО сбой реккурента {user.user_id}',
                comment=f'{ex}'
            )


# проверка оплаты по ю кассе
async def check_pay_yoo():
    bills = await db.get_all_pay_yoo()
    for bill in bills:
        payment = Payment.find_one(bill.pay_id)
        if payment.paid:
            user_info = await db.get_user_info(user_id=bill.user_id)
            try:
                new_kick_date = add_months (count_months=bill.tariff, kick_date=user_info.kick_date)
                await db.update_user_info (
                    user_id=user_info.user_id,
                    kick_date=new_kick_date,
                    last_pay_id=payment.id,
                    status=UserStatus.SUB.value,
                    tariff=str(bill.tariff),
                    recurrent=True if bill.tariff == 1 else False
                )

                text = (f'✅ Оплата прошла успешно, подписка продлена до {new_kick_date.strftime(conf.date_format)}\n\n'
                        f'Нажмите кнопку "🔙 На главный экран" ')

                await db.reg_action (
                    user_id=bill.user_id,
                    status='successfully',
                    action='оплата подписки Юкасса',
                    comment=f'Тариф {bill.tariff}'
                )

            except Exception as ex:
                log_error(ex)
                text = '❗️Ошибка оплаты. Обратитесь в техподдержку'
                await db.reg_action (
                    user_id=user_info.user_id,
                    status='failed',
                    action='оплата подписки Юкасса',
                    comment=f'{ex[:200]}'
                )
                # photo_id = await db.get_random_photo_id ()
                # await bot.send_photo(
                #     chat_id=user_info.user_id,
                #     photo=photo_id.photo_id,
                #     caption=text,
                #     reply_markup=)

            if user_info.status == UserStatus.SUB.value:
                try:
                    photo_id = await db.get_random_photo_id()
                    photo = InputMediaPhoto(media=photo_id.photo_id, caption=text)
                    await bot.edit_message_media(
                        media=photo,
                        chat_id=bill.chat_id, message_id=bill.msg_id, reply_markup=kb.back_start_button())
                except Exception as ex:
                    logging.warning(ex)
            else:
                unban = await bot.unban_chat_member(chat_id=conf.channel_id, user_id=bill.user_id, only_if_banned=True)
                if unban:
                    await db.reg_action (user_id=user_info.user_id, status='successfully', action='разбан')

                link = await bot.create_chat_invite_link(conf.channel_id, member_limit=1)
                await db.reg_action (
                    user_id=user_info.user_id,
                    status='successfully',
                    action='создана ссылка',
                    comment=link.invite_link
                )

                try:
                    photo_id = await db.get_random_photo_id()
                    photo = InputMediaPhoto(media=photo_id.photo_id, caption=text)
                    await bot.edit_message_media(
                        media=photo,
                        chat_id=bill.chat_id,
                        message_id=bill.msg_id,
                        reply_markup=kb.succeeded_link_kb(link.invite_link)
                    )
                except Exception as ex:
                    log_error (ex)
                    await db.reg_action (
                        user_id=user_info.user_id,
                        status='failed',
                        action='Сообщение подтверждения оплаты не изменено',
                        comment=f'ex: {ex}'
                    )

            await db.del_from_yoo_temp(bill.id)

            try:
                amount = await db.get_amount(bill.tariff)
                await db.save_bill (user_id=bill.user_id, total_amount=amount, payment_id=payment.id)
                await db.reg_action (
                    user_id=bill.user_id,
                    status='successfully',
                    action='оплата сохранена',
                    comment=payment.id
                )
            except Exception as ex:
                log_error (ex)
                await db.reg_action (
                    user_id=bill.user_id,
                    status='failed',
                    action='оплата сохранена',
                    comment='Оплата прошла, но не записана в бд'
                )

        else:
            time_msc = bill.time.astimezone (conf.tz)
            time_del = time_msc + timedelta(hours=1)

            if datetime.now(conf.tz) > time_del:
                text = (f'❗️Срок действия ссылки истёк.\n'
                        f'Чтобы оплатить нажмите нажмите 👉 вернуться в начало и снова перейдите к оплате')

                try:
                    photo_id = await db.get_random_photo_id()
                    photo = InputMediaPhoto(media=photo_id.photo_id, caption=text)
                    await bot.edit_message_media(
                        media=photo,
                        chat_id=bill.chat_id,
                        message_id=bill.msg_id,
                        reply_markup=kb.back_start_button())

                except Exception as ex:
                    logging.warning(f'scheduler 235 {ex}')

                await db.del_from_yoo_temp (bill.id)
                await db.reg_action (
                    user_id=bill.user_id,
                    status='successfully',
                    action='просрочена ссылка на оплату',
                    comment=f'Время удаления: {datetime.now(conf.tz)}\n'
                            f'Срок жизни ссылки: {time_del}'
                )
