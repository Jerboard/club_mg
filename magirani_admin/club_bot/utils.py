from datetime import datetime, date

from magirani_admin.settings import BASE_DIR, DATE_FORMAT, TZ


# добавить месяцы к дате
def add_months(count_mounts: int, kick_date: date) -> date:
    start_date = datetime.now(conf.tz).date()

    if not kick_date:
        pass
    elif start_date < kick_date:
        start_date = kick_date

    new_day = start_date.day
    new_mount = start_date.month + count_mounts
    new_year = start_date.year

    if new_mount > 12:
        new_mount = new_mount - 12
        new_year += 1

    if new_day > 28 and new_mount == 2:
        new_day = 28
    elif new_day > 30 and new_mount in [4, 6, 9, 11]:
        new_day = 30

    return datetime.strptime(f'{new_day}.{new_mount}.{new_year}', DATE_FORMAT).date()
