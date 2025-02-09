from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

import db
import utils as ut
from config import conf
from db.funnel import Funnel
from data.base_data import periods, groups_users
from enums import BaseCB, AdminCB, FunnelCB, FunnelAction, Action


# админская клавиатура
def get_first_admin_kb(only_state: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if not only_state:
        kb.button(text='✉️ Отправить сообщение', callback_data=AdminCB.SEND_MESSAGES_1.value)
        kb.button(text=f'📅 Воронка', callback_data=f'{FunnelCB.MENU.value}')
        kb.button(text='💾 Сохранённые сообщения', callback_data=AdminCB.SAVE_MESSAGES_1.value)
        kb.button(text='🗑 Удалить пользователя', callback_data=AdminCB.DEL_USER_1.value)
    kb.button(text='Войти как пользователь', callback_data=BaseCB.BACK_COM_START.value)
    return kb.adjust(1).as_markup()


# список сохранённых сообщений
def get_alter_pay_methods_kb(methods: tuple[db.UserAlterPayMethodRow]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='🔙Назад', callback_data=f'{AdminCB.ADD_MONTHS_2.value}:del')
    for method in methods:
        kb.button (text=method.name, callback_data=f'{AdminCB.ADD_MONTHS_1.value}:{method.id}')
    return kb.adjust (1).as_markup ()


# добавить месяцев
def get_add_months_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button (text=f'1 Месяц', callback_data=f'{AdminCB.ADD_MONTHS_2.value}:1')
    kb.button (text=f'3 месяца', callback_data=f'{AdminCB.ADD_MONTHS_2.value}:3')
    kb.button (text=f'6 месяцев', callback_data=f'{AdminCB.ADD_MONTHS_2.value}:6')
    kb.button (text=f'1 год', callback_data=f'{AdminCB.ADD_MONTHS_2.value}:12')
    kb.button (text='❌ Отмена', callback_data=f'{AdminCB.ADD_MONTHS_2.value}:del')
    return kb.adjust (2).as_markup ()


# админская клавиатура отправки сообщений
def get_send_message_kb(group_recip, group_time) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if group_recip == '0':
        kb.button (text=f'✔️ {groups_users[0]}', callback_data=f'{AdminCB.SEND_MESSAGES_2.value}:1')
        kb.button (text=f'{groups_users[1]}', callback_data=f'{AdminCB.SEND_MESSAGES_2.value}:1')
    elif group_recip == '1':
        kb.button (text=f'{groups_users[0]}', callback_data=f'{AdminCB.SEND_MESSAGES_2.value}:0')
        kb.button (text=f'✔️ {groups_users[1]}', callback_data=f'{AdminCB.SEND_MESSAGES_2.value}:0')
    else:
        kb.button (text=f'{groups_users[0]}', callback_data=f'{AdminCB.SEND_MESSAGES_2.value}:0')
        kb.button (text=f'{groups_users[1]}', callback_data=f'{AdminCB.SEND_MESSAGES_2.value}:1')
    # if group_recip == '0':
    #     kb.button (text=f'✔️ Гости', callback_data=f'{AdminCB.SEND_MESSAGES_2.value}:1')
    #     kb.button (text=f'Без доступа', callback_data=f'{AdminCB.SEND_MESSAGES_2.value}:1')
    # elif group_recip == '1':
    #     kb.button (text=f'Гости', callback_data=f'{AdminCB.SEND_MESSAGES_2.value}:0')
    #     kb.button (text=f'✔️ Без доступа', callback_data=f'{AdminCB.SEND_MESSAGES_2.value}:0')
    # else:
    #     kb.button (text=f'Гости', callback_data=f'{AdminCB.SEND_MESSAGES_2.value}:0')
    #     kb.button (text=f'Без доступа', callback_data=f'{AdminCB.SEND_MESSAGES_2.value}:1')

    kb.button (text='📆 Периоды', callback_data=AdminCB.SEND_MESSAGES_3.value)

    if group_time is None:
        select = None
    else:
        select = int(group_time)

    for k, v in periods.items():
        name = f'✔ {v["name"]}' if select == k or select == 7 else v["name"]
        kb.button (text=name, callback_data=f'{AdminCB.SEND_MESSAGES_4.value}:{k}')

    kb.button (text='📤 Отправить', callback_data=AdminCB.SEND_MESSAGES_5.value)
    kb.button (text='💾 Сохранить', callback_data=f'{AdminCB.SEND_MESSAGES_6.value}:{Action.SAVE.value}')
    kb.button (text='💾 Сохранить и назад', callback_data=f'{AdminCB.SEND_MESSAGES_6.value}:{Action.DEL.value}')
    kb.button (text='📅 Создать воронку', callback_data=f'{AdminCB.SEND_MESSAGES_6.value}:{Action.FUNNEL.value}')
    kb.button (text='🗑 Назад без сохранения', callback_data=AdminCB.SEND_MESSAGES_8.value)

    return kb.adjust(2, 1, 2, 2, 2, 1).as_markup()


# подтвердить отправку сообщения пользователям
def accept_send_message_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder ()
    kb.button (text='✅ Подтвердить', callback_data=AdminCB.SEND_MESSAGES_7.value)
    kb.button (text='💾 Сохранить сообщение', callback_data=f'{AdminCB.SEND_MESSAGES_6.value}:{Action.SAVE.value}')
    kb.button (text='🗑 Назад без сохранения', callback_data=AdminCB.SEND_MESSAGES_8.value)
    return kb.adjust (1).as_markup ()


# возвращает к админскому главному экрану
def back_admin_menu_kb(is_back: bool = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder ()
    if is_back:
        kb.button (text='🔙 Назад', callback_data=AdminCB.BACK_ADMIN_START.value)
    else:
        kb.button (text='🔙 Продолжить', callback_data=AdminCB.BACK_ADMIN_START.value)
    return kb.adjust (1).as_markup ()


# список сохранённых сообщений
def get_save_message_kb(messages: tuple[db.SaveMessagesRow]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder ()
    kb.button (text='🔙 Назад', callback_data=AdminCB.BACK_ADMIN_START.value)

    for message in messages:
        kb.button (text=message.title or 'НД', callback_data=f'{AdminCB.SAVE_MESSAGES_2.value}:{message.id}:0')
        kb.button (text='🗑', callback_data=f'{AdminCB.DEL_MESSAGE_1.value}:{message.id}')
    return kb.adjust (1, 2).as_markup ()


# основное меню воронки
def get_funnel_menu_kb(funnels: list[Funnel.FullRow]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder ()
    kb.button (text='🔙 Назад', callback_data=AdminCB.BACK_ADMIN_START.value)
    kb.button(text='➕ Добавить', callback_data=AdminCB.SAVE_MESSAGES_1.value)
    for funnel in funnels:
        kb.button(text=funnel.title, callback_data=f'{FunnelCB.VIEW.value}:{funnel.funnel_id}')

    return kb.adjust (2, 1).as_markup ()


# воронка изменить
def get_funnel_edit_kb(funnel: Funnel.FullRow) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder ()
    next_start = ut.get_next_start_date(next_start_date=funnel.next_start_date, next_start_time=funnel.next_start_time)

        # next_start_time = funnel.next_start.astimezone(conf.tz)
        # # next_start_time = funnel.next_start
    time_start_str = f'{next_start.hour:02}:{next_start.minute:02}'

    kb.button (text='🔙 Назад', callback_data=FunnelCB.MENU.value)
    kb.button(
        text=f'🖍 Редактировать сообщение',
        callback_data=f'{AdminCB.SAVE_MESSAGES_2.value}:{funnel.save_msg_id}:{funnel.funnel_id}'
    )

    mark_active = ('✅ Активно', 0) if funnel.is_active else ('❌ Не активно', 1)
    kb.button(
        text=mark_active[0],
        callback_data=f'{FunnelCB.EDIT.value}:{FunnelAction.ACTIVE.value}:{funnel.funnel_id}:{mark_active[1]}'
    )
    kb.button(
        text=f'Период: {funnel.period_day}',
        callback_data=f'{FunnelCB.EDIT.value}:{FunnelAction.PERIOD.value}:{funnel.funnel_id}:{funnel.period_day}'
    )
    kb.button(
        text=f'Время отправки: {time_start_str}',
        callback_data=f'{FunnelCB.EDIT.value}:{FunnelAction.TIME.value}:{funnel.funnel_id}:0'
    )
    kb.button(text='📤 Отправить сейчас', callback_data=f'{FunnelCB.SEND.value}:{funnel.funnel_id}')
    kb.button (text='🗑 Удалит', callback_data=f'{FunnelCB.EDIT.value}:{FunnelAction.DEL.value}:{funnel.funnel_id}:0')

    return kb.adjust (1).as_markup ()


# воронка изменить
def get_funnel_back_view_kb(funnel_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder ()
    kb.button (text='🔙 Назад', callback_data=f'{FunnelCB.VIEW.value}:{funnel_id}')
    return kb.adjust(1).as_markup()
