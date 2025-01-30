import telebot
import logging
import traceback
import os

from datetime import datetime

from magirani_admin.settings import BASE_DIR, DEBUG, BOT_TOKEN, TZ

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='html')


def log_error(message, with_traceback: bool = True):
    try:
        now = datetime.now(conf.tz)
        log_folder = now.strftime ('%m-%Y')
        log_path = os.path.join(BASE_DIR, 'club_bot', 'bot', 'bot_log', log_folder)

        if not os.path.exists(log_path):
            os.makedirs(log_path)

        log_file_path = os.path.join(log_path, f'{now.day}.log')
        logging.basicConfig (level=logging.WARNING, filename=log_file_path, encoding='utf-8')
        if with_traceback:
            ex_traceback = traceback.format_exc()
            logging.warning(f'=====\n{now}\n{ex_traceback}\n{message}\n=====')
        else:
            logging.warning(f'=====\n{now}\n{message}\n=====')

    except:
        pass


