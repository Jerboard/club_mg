from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from club_bot.enums import BaseCB


# возвращает на главный экран
def get_back_start_kb():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text='🔙 На главный экран', callback_data=BaseCB.BACK_COM_START.value)
    )


# клавиатура после оплаты со ссылкой
def get_succeeded_link_kb(link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup (row_width=1).add (
        InlineKeyboardButton (text='🔗 Перейти в канал', url=link),
        InlineKeyboardButton (text='🔙 На главный экран', callback_data=BaseCB.BACK_COM_START.value),
    )

