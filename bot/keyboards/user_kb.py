from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

import db
from config import conf
from enums import BaseCB, UserCB


# команда старт
def com_start_kb(keyboard_type: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button (text='Перейти к оплате', callback_data=f'{UserCB.PAY_YOOKASSA_1.value}:0')

    if keyboard_type == 0:
        kb.button(text='О клубе', url=conf.info_url)
    elif keyboard_type == 1:
        kb.button (text='Личный кабинет', callback_data=UserCB.MY_ACCOUNT.value)
    else:
        kb.button (text='Перейти в канал', url=conf.channel_link)

    kb.button (text='Техподдержка', callback_data=UserCB.SUPPORT_0.value)
    if keyboard_type != 0:
        kb.button (text='🔄 Обновить', callback_data=BaseCB.BACK_COM_START.value)

    return kb.adjust(1).as_markup()


# По кнопке техподдержка
def get_support_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button (text='Доступ по EMAIL', callback_data=UserCB.SUPPORT_1.value)
    kb.button (text='Написать в техподдержку', url='https://t.me/Magirani_support')
    kb.button (text='🔙 Вернуться назад', callback_data=BaseCB.BACK_COM_START.value)
    return kb.adjust(1).as_markup()


# возвращает на главный экран
def accept_email() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder ()
    kb.button (text='✔️ Подтвердить', callback_data=UserCB.PAY_YOOKASSA_0.value)
    kb.button (text='✏️ Изменить', callback_data=f'{UserCB.PAY_YOOKASSA_1.value}:1')
    kb.button (text='🔙 На главный экран', callback_data=BaseCB.BACK_COM_START.value)
    return kb.adjust (1).as_markup ()


# выбор тарифа
def select_tariff_kb(info: db.InfoRow) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button (text=f'1 Месяц: {info.cost_1} ₽', callback_data=f'{UserCB.PAY_YOOKASSA_2.value}:1:{info.cost_1}')
    kb.button (text=f'✨️ 3 месяца {info.cost_3} ₽ ✨️', callback_data=f'{UserCB.PAY_YOOKASSA_2.value}:3:{info.cost_3}')
    kb.button (text=f'6 месяцев {info.cost_6} ₽', callback_data=f'{UserCB.PAY_YOOKASSA_2.value}:6:{info.cost_6}')
    kb.button (text=f'🔮 1 год {info.cost_12} ₽ 🔮', callback_data=f'{UserCB.PAY_YOOKASSA_2.value}:12:{info.cost_12}')
    kb.button (text='🔙 Вернуться назад', callback_data=BaseCB.BACK_COM_START.value)
    return kb.adjust (1).as_markup ()


# Кнопка отказаться от подписки
def get_unsubscribe_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button (text='🔙 Вернуться назад', callback_data=BaseCB.BACK_COM_START.value)
    kb.button (text='🔗 Перейти в канал', url=conf.channel_link)
    kb.button (text='Отказаться от подписки', callback_data=UserCB.UNSUBSCRIBE.value)
    return kb.adjust (1).as_markup ()


# ссылка на оплату в юкассе
def pay_yookassa_kb(amount: int, link: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder ()
    kb.button (text=f'💳 Оплатить {amount} ₽', url=link)
    kb.button (text='🔙 Назад', callback_data=UserCB.PAY_YOOKASSA_0.value)
    return kb.adjust (1).as_markup ()


# клавиатура после оплаты со ссылкой
def succeeded_link_kb(link: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder ()
    kb.button (text='🔗 Перейти в канал', url=link)
    kb.button (text='🔙 На главный экран', callback_data=BaseCB.BACK_COM_START.value)
    return kb.adjust (1).as_markup ()


# удаляет сообщение рассылки у пользователя
def del_message_user():
    kb = InlineKeyboardBuilder ()
    kb.button (text='✅ Ок', callback_data=BaseCB.BACK_COM_START.value)
    return kb.adjust (1).as_markup ()


# Для забаненых
def get_ban_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button (text='Написать в техподдержку', url='https://t.me/Magirani_support')
    return kb.adjust(1).as_markup()
