from datetime import date

from db.funnel import Funnel
from data.base_data import periods, groups_users
from .datetime_utils import get_next_start_date
from config import conf


# текст приветствия
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


# текст воронки
def get_funnel_text(funnels: list[Funnel.FullRow]) -> str:
    text = ''
    sep = '\n---\n'
    for funnel in funnels:
        next_start = get_next_start_date(next_start_date=funnel.next_start_date, next_start_time=funnel.next_start_time)
        # next_start = f'{funnel.next_start.astimezone(conf.tz).strftime(conf.datetime_format)}' if funnel.next_start else '-'
        group = groups_users[int(funnel.group_recip)] if funnel.group_recip else '-'
        period = periods[funnel.period_id]["name"] if funnel.period_id else '-'
        is_active = '🟢' if funnel.is_active else '🔴'
        text += (
            f'{is_active} {funnel.title}\n'
            f'<b>След. старт</b>: {next_start} \n'
            f'<b>Группа</b>: {group} {period}'
            f'{sep}'
        )

    return text
