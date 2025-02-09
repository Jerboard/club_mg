from enums import Unit


periods = {
    1: {'name': '0-7 дней', 'start': 7, 'end': 0, 'unit': 'days'},
    2: {'name': '7-14 дней', 'start': 14, 'end': 7, 'unit': 'days'},
    3: {'name': '15-30 дней', 'start': 30, 'end': 15, 'unit': 'days'},
    4: {'name': '1 - 3 месяца', 'start': 3, 'end': 1, 'unit': 'mounts'},
    5: {'name': '3 - 6 месяцев', 'start': 6, 'end': 3, 'unit': 'mounts'},
    6: {'name': 'Более 6 месяцев', 'start': 120, 'end': 6, 'unit': 'mounts'},
    7: {'name': 'Все периоды', 'start': 120, 'end': 0, 'unit': 'mounts'}
}


groups_users = {
    0: '️Гости',
    1: 'Без доступа',
}
