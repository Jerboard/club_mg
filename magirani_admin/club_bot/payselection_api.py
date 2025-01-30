import requests
import json
import random
import hmac
import hashlib

from magirani_admin.settings import ps_pay_data
from .bot.base import log_error
from .models import PaymentPS


# отказ от рекуррена
async def stop_recurrent(recurring_id: str) -> bool:
    try:
        payment = PaymentPS.objects.filter (recurring_id=recurring_id).first ()
        card_type = payment.card_type

        url_tail = '/payments/recurring/unsubscribe'
        url = f"https://gw.payselection.com{url_tail}"
        x_site_id = ps_pay_data ['shop_id'] [card_type]
        site_secret_key = ps_pay_data ['secret_key'] [card_type]
        x_request_id = str (random.randint (100000, 999999))

        request_body = {
            "RecurringId": recurring_id
        }
        json_body = json.dumps (request_body)
        signature_string = f"POST\n{url_tail}\n{x_site_id}\n{x_request_id}\n{json_body}"

        # Вычислите сигнатуру запроса
        signature = hmac.new (
            key=site_secret_key.encode (),
            msg=signature_string.encode (),
            digestmod=hashlib.sha256,
        ).hexdigest ()

        # Заголовки запроса
        headers = {
            'Content-Type': 'application/json',
            'X-SITE-ID': x_site_id,
            'X-REQUEST-ID': x_request_id,
            'X-REQUEST-SIGNATURE': signature
        }

        response = requests.post(url=url, headers=headers, json=request_body)

        if response.status_code == 201:
            return True
        else:
            log_error(f'Сбой отмены рекуррента:\n{response.text}', with_traceback=False)
            return False

    except Exception as ex:
        log_error (ex)
