import os

from pytz import timezone


class Config():
    debug = bool(int(os.getenv('DEBUG')))

    if debug:
        token = os.getenv("TEST_TOKEN")
        db_host = os.getenv('DB_HOST')
    else:
        token = os.getenv("TOKEN")
        db_host = os.getenv('DB_HOST_LOCAL')
        
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('POSTGRES_DB')
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_url = f'postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    
    tz = timezone('Europe/Moscow')

    bot_name = os.getenv('BOT_NAME')
    support_chat_id = int(os.getenv('SUPPORT_CHAT_ID'))
    channel_id = int(os.getenv('CHANNEL_ID'))
    channel_name = os.getenv('CHANNEL_NAME')
    bot_link = os.getenv('BOT_LINK')
    channel_link = os.getenv('CHANNEL_LINK')
    info_url = os.getenv('INFO_URL')
    yoo_account_id = int(os.getenv('YOO_ACCOUNT_ID'))
    yoo_secret_key = os.getenv('YOO_SECRET_KEY')

    date_format = '%d.%m.%Y'
    time_format = '%H:%M'
    datetime_format = '%H:%M %d.%m.%Y'
    free_email_id = 11111


conf = Config()
