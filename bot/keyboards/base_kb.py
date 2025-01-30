from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from enums import BaseCB, UserCB


# возвращает на главный экран
def back_start_button():
    kb = InlineKeyboardBuilder()
    kb.button(text='🔙 На главный экран', callback_data=BaseCB.BACK_COM_START.value)
    return kb.adjust(1).as_markup()


# Отменяет действие
def get_close_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='🔙 Назад', callback_data=BaseCB.CLOSE.value)
    return kb.adjust(1).as_markup()