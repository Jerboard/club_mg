from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

import asyncio

from db.funnel import Funnel
import keyboards as kb
from config import conf
from init import dp, log_error
import utils as ut
from enums import FunnelCB, FunnelAction, BaseStatus


# старт воронки меню
@dp.callback_query (lambda cb: cb.data.startswith(FunnelCB.MENU.value))
async def funnel_menu(cb: CallbackQuery, state: FSMContext):
    funnels = await Funnel.get()

    text = ut.get_funnel_text(funnels) if funnels else '❌ У вас ещё нет воронок'
    # await cb.message.answer(text=text, reply_markup=kb.get_funnel_menu_kb(funnels))
    try:
        await cb.message.edit_text(text=text, reply_markup=kb.get_funnel_menu_kb(funnels))
    except Exception as ex:
        await cb.message.answer(text=text, reply_markup=kb.get_funnel_menu_kb(funnels))


# Изменить воронку
@dp.callback_query (lambda cb: cb.data.startswith(FunnelCB.VIEW.value))
async def funnel_view(cb: CallbackQuery, state: FSMContext):
    _, funnel_id_str = cb.data.split(':')
    funnel_id = int(funnel_id_str)

    await ut.get_funnel_view(funnel_id=funnel_id, chat_id=cb.message.chat.id, msg_id=cb.message.message_id)


# Изменения
@dp.callback_query (lambda cb: cb.data.startswith(FunnelCB.EDIT.value))
async def funnel_edit(cb: CallbackQuery, state: FSMContext):
    print(f'cb.data: {cb.data}')
    _, action, funnel_id_str, funnel_value = cb.data.split(':')
    funnel_id = int(funnel_id_str)

    if action == FunnelAction.ACTIVE.value:
        funnel = await Funnel.get_by_id(funnel_id=funnel_id)
        is_active = bool(int(funnel_value))

        if not funnel.period_day and is_active:
            await cb.answer('❗️ Не задан период', show_alert=True)
            return

        await Funnel.edit(funnel_id=funnel_id, is_active=is_active)

        if is_active:
            await ut.add_funnel_job(funnel_id=funnel_id)
        else:
            await ut.del_funnel_job(funnel_id=funnel_id)

        await ut.get_funnel_view(funnel_id=funnel_id, chat_id=cb.message.chat.id)

    elif action == FunnelAction.PERIOD.value:
        await cb.answer('📅 Отправьте период рассылки в днях от 1 до 365', show_alert=True)
        await state.set_state(BaseStatus.EDIT_FUNNEL.value)
        await state.update_data(data={'action': action, 'funnel_id': funnel_id})
        await cb.message.edit_reply_markup(reply_markup=kb.get_funnel_back_view_kb(funnel_id))

    elif action == FunnelAction.TIME.value:
        await cb.answer(f'⏰ Отправьте время рассылки в формате {conf.time_format.replace("%", "")}', show_alert=True)
        await state.set_state(BaseStatus.EDIT_FUNNEL.value)
        await state.update_data(data={'action': action, 'funnel_id': funnel_id})
        await cb.message.edit_reply_markup(reply_markup=kb.get_funnel_back_view_kb(funnel_id))

    elif action == FunnelAction.DEL.value:
        await ut.del_funnel_job(funnel_id=funnel_id)
        await Funnel.del_funnel(funnel_id=funnel_id)
        await cb.message.delete()
        await funnel_menu(cb, state)

    else:
        await cb.answer('‼️ Что-то сломалось воронка не изменена', show_alert=True)


# изменяет цифры в настройках воронки
@dp.message (StateFilter(BaseStatus.EDIT_FUNNEL.value))
async def edit_funnel_msg(msg: Message, state: FSMContext):
    data = await state.get_data()

    error_text = None

    if data['action'] == FunnelAction.PERIOD.value:
        if not msg.text.isdigit():
            error_text = '‼️ Период должен быть целым числом'

        else:
            period = int(msg.text)
            period = 365 if period > 365 else period
            period = 1 if period < 1 else period

            start_date = datetime.now() + timedelta(days=period)

            # funnel = await Funnel.get_by_id(funnel_id=data['funnel_id'])
            #
            # next_start_old = funnel.next_start if funnel.next_start else datetime.now(conf.tz)
            # next_start = ut.get_next_start_date(period=period, old_start_date=next_start_old)

            await Funnel.edit(funnel_id=data['funnel_id'], period_day=period, next_start_date=start_date.date())

    elif data['action'] == FunnelAction.TIME.value:
        try:
            time = datetime.strptime(msg.text, conf.time_format)

            # funnel = await Funnel.get_by_id(funnel_id=data['funnel_id'])
            # next_start = ut.get_next_start_date(start_date=funnel.next_start, time_str=msg.text)

            await Funnel.edit(funnel_id=data['funnel_id'], next_start_time=time.time())

        except ValueError as ex:
            error_text = f'‼️ Время должно быть в формате {conf.time_format.replace("%", "")}'
            log_error(ex)

        except Exception as ex:
            error_text = '‼️ Что-то сломалось воронка не изменена'
            log_error(ex)

    else:
        error_text = '‼️ Что-то сломалось воронка не изменена'

    if error_text:
        sent = await msg.answer(error_text)
        await asyncio.sleep(3)
        await sent.delete()

    else:
        await state.clear()
        await ut.get_funnel_view(funnel_id=data['funnel_id'], chat_id=msg.chat.id, msg_id=msg.message_id)


# Отправить сообщение
@dp.callback_query (lambda cb: cb.data.startswith(FunnelCB.SEND.value))
async def funnel_send(cb: CallbackQuery, state: FSMContext):
    _, funnel_id_str = cb.data.split(':')
    funnel_id = int(funnel_id_str)

    # await cb.message.delete()
    await ut.funnel_malling(funnel_id)
