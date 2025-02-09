from django.http import HttpRequest, JsonResponse
from datetime import datetime, timedelta
import json

from club_bot import bot
from club_bot.models import PaymentPS, User, ActionJournal
from club_bot.utils import add_months
from club_bot.enums import RecurrentStatus, PaymentStatus, UserStatus
from club_bot.bot.base import log_error
from club_bot.payselection_api import stop_recurrent




# списание обычной оплаты
def simple_payment(request: HttpRequest):
    response_info = {'info': 'bad request'}

    text = f'simple_payment\n{request.body}'
    log_error (message=text, with_traceback=False)
    try:
        request_data: dict = json.loads(request.body)
        if request_data['Event'] == "Payment":
            user_id, add_mounts_count, tariff, chat_id, message_id = map(int, request_data['Description'].split(':'))
            order_id = request_data['OrderId']
            rebill_id = request_data.get ('RebillId')
            # recurring_id = request_data.get ('RecurringId')

            check_payment = PaymentPS.objects.filter (transaction_id=request_data['TransactionId']).first ()
            if check_payment:
                log_error(f'Повторная оплата:\n{request_data}', with_traceback=False)
                return JsonResponse({'info': 'successfully'})

            payment = PaymentPS.objects.filter (order_id=order_id).first ()

            payment.status = PaymentStatus.SUCCESSFULLY.value
            payment.transaction_id = request_data['TransactionId']
            payment.rebill_id = rebill_id
            payment.save()

            user_info = User.objects.filter (user_id=user_id).first ()

            new_kick_date = add_months(count_mounts=add_mounts_count, kick_date=user_info.kick_date)
            user_status = user_info.status
            user_info.kick_date = new_kick_date
            user_info.tariff = tariff
            user_info.status = 'sub'
            user_info.recurrent = True if tariff == '1500' else False
            user_info.alarm_2_day = False
            user_info.save()

            # photo = PhotosTable.objects.order_by("?").first()

            bot.success_payment(
                user_id=user_id,
                message_id=message_id,
                new_kick_date=new_kick_date,
                user_status=user_status
            )

            new_node = ActionJournal (
                time=datetime.now (),
                user_id=user_id,
                status=PaymentStatus.SUCCESSFULLY.value,
                action='Оплата'
            )
            new_node.save ()

        elif request_data['Event'] == "Fail":
            user_id, add_mounts_count, tariff, chat_id, message_id = map (int, request_data ['Description'].split (':'))
            new_node = ActionJournal(
                time=datetime.now(),
                user_id=user_id,
                status=PaymentStatus.FAILED.value,
                action='Оплата',
                comment=(f'{request_data.get("Brand")} {request_data.get("Bank")} '
                         f'{request_data.get("Amount")} {request_data.get("Currency")}\n'
                         f'{request_data.get("ClientMessage")}')
            )
            new_node.save()

        # elif request_data['Event'] == "3DS":
        #     payment = PaymentPS.objects.filter (order_id=request_data['OrderId']).first ()
        #     payment.transaction_id = request_data ['TransactionId']
        #     payment.save ()

        response_info = {'info': 'successfully'}

    except Exception as ex:
        log_error(ex)

    finally:
        return JsonResponse(response_info)


# списание реккурента
def recurrent_payment(request: HttpRequest):
    response_info = {'info': 'bad request'}

    text = f'recurrent_payment\n{request.body}'
    log_error (message=text, with_traceback=False)

    status = None
    comment = None
    try:
        request_data: dict = json.loads(request.body)
        user_id = int(request_data['AccountId'])
        if request_data['RecurringStatus'] == RecurrentStatus.NEW.value:
            payment = PaymentPS.objects.filter (order_id=request_data ['Description']).first ()
            payment.recurring_id = request_data.get ('RecurringId')
            payment.save ()

            user_info = User.objects.filter (user_id=user_id).first ()
            if user_info.recurrent:
                stop_recurrent(recurring_id=user_info.last_pay_id)

            user_info.recurrent = True
            user_info.last_pay_id = request_data.get ('RecurringId')
            user_info.save ()

            status = PaymentStatus.SUCCESSFULLY.value
            comment = 'Новый рекуррент'

        elif request_data['RecurringStatus'] == RecurrentStatus.ACTIVE.value:
            user_info = User.objects.filter (user_id=user_id).first ()

            new_kick_date = add_months (count_mounts=1, kick_date=user_info.kick_date)
            user_info.kick_date = new_kick_date
            user_info.alarm_2_day = False
            user_info.save ()

            new_payment = PaymentPS(
                user_id=user_id,
                created_at=datetime.now(),
                amount=request_data.get('Amount'),
                status=PaymentStatus.SUCCESSFULLY.value,
                rebill_id=request_data.get('RebillId'),
                recurring_id=request_data.get('RecurringId'),
                transaction_id=request_data["Recurrent"]["TransactionId"]
            )
            new_payment.save()

            status = PaymentStatus.SUCCESSFULLY.value

        elif request_data['RecurringStatus'] == RecurrentStatus.OVERDUE.value:
            text = 'Неудачное списание рекуррента. Пополните баланс и т.д.'

            bot.send_info_message(user_id=user_id, text=text)

            status = PaymentStatus.FAILED.value

        elif request_data['RecurringStatus'] == RecurrentStatus.TERMINATED.value:
            user_info = User.objects.filter (user_id=user_id).first ()

            user_info.status = UserStatus.NOT_SUB.value
            user_info.recurrent = False
            user_info.save ()

            text = 'Неудачное списание рекуррента. Ваше членство в клубе приостановлено и бла-бла'

            bot.send_info_message (user_id=user_id, text=text)

            status = PaymentStatus.FAILED.value
            comment = 'Отмена рекуррента'

        else:
            pass

        if status:
            new_node = ActionJournal (
                time=datetime.now (),
                user_id=user_id,
                status=status,
                action='Списание рекуррента',
                comment=comment
            )
            new_node.save ()

        response_info = {'info': 'successfully'}

    except Exception as ex:
        log_error (ex)

    finally:
        return JsonResponse (response_info)


# удачная оплата с подключением реккурента
'''
{
  "RebillId": "PS00000412176545",
  "Amount": "10.00",
  "Currency": "RUB",
  "Description": "5772948261",
  "WebhookUrl": "https://webhook.site/c32e0033-ee49-40cc-a5ce-18afb610b832",
  "AccountId": "5772948261",
  "Email": "dgushch@gmail.com",
  "Interval": "1",
  "Period": "month",
  "MaxPeriods": "999",
  "RecurringId": "330150",
  "ReceiptData": {},
  "Event": "RegisterRecurring",
  "RecurringStatus": "new",
  "StartDate": "2024-05-03T14:02+0000"
}
'''


# удачная снятие реккурента
'''
{
  "RebillId": "PS00000411124013",
  "Amount": "15.00",
  "Currency": "RUB",
  "Description": "tg_user_id",
  "WebhookUrl": "https://webhook.site/c32e0033-ee49-40cc-a5ce-18afb610b832",
  "AccountId": "order63",
  "Interval": "1",
  "Period": "day",
  "MaxPeriods": "15",
  "RecurringId": "329183",
  "Recurrent": {
    "TransactionId": "PS00000412161345",
    "TransactionState": "success"
  },
  "Event": "ChangeRecurringState",
  "RecurringStatus": "active",
  "StartDate": "2024-04-03T13:42+0000",
  "LatestPay": "2024-04-03T13:42+0000"
}
'''
# неудачное снятие реккурента
'''
{
  "RebillId": "PS00000411124013",
  "Amount": "15.00",
  "Currency": "RUB",
  "Description": "tg_user_id",
  "WebhookUrl": "https://webhook.site/c32e0033-ee49-40cc-a5ce-18afb610b832",
  "AccountId": "order63",
  "Interval": "1",
  "Period": "day",
  "MaxPeriods": "15",
  "RecurringId": "329183",
  "Recurrent": {
    "TransactionId": "PS00000413369679",
    "TransactionState": "declined",
    "TransactionStateDetails": {
      "Code": "",
      "Description": ""
    }
  },
  "Event": "ChangeRecurringState",
  "RecurringStatus": "overdue",
  "StartDate": "2024-04-03T13:42+0000",
  "LatestPay": "2024-04-03T13:42+0000"
}
'''

# отмена реккурена
'''
{
  "RebillId": "PS00000411124013",
  "Amount": "15.00",
  "Currency": "RUB",
  "Description": "tg_user_id",
  "WebhookUrl": "https://webhook.site/c32e0033-ee49-40cc-a5ce-18afb610b832",
  "AccountId": "order63",
  "Interval": "1",
  "Period": "day",
  "MaxPeriods": "15",
  "RecurringId": "329183",
  "Recurrent": {
    "TransactionId": "PS00000415548067",
    "TransactionState": "declined",
    "TransactionStateDetails": {
      "Code": "",
      "Description": ""
    }
  },
  "Event": "ChangeRecurringState",
  "RecurringStatus": "terminated",
  "StartDate": "2024-04-03T13:42+0000",
  "LatestPay": "2024-04-03T13:42+0000"
}
'''

# неудачная оплата
'''
  "Event": "Fail",
  "Amount": "10.00",
  "Currency": "RUB",
  "DateTime": "09.04.2024 20.30.35",
  "IsTest": 0,
  "Email": "dgushch@gmail.com",
  "Brand": "MASTERCARD",
  "Bank": "SBERBANK OF RUSSIA",
  "CountryCodeAlpha2": "RU",
  "TransactionId": "PS00000418936538",
  "OrderId": "524275902-4000-2",
  "Description": "524275902:3:4000:524275902:415",
  "CustomFields": "ReturnUrl=https%3A//t.me/Magirani_projects_bot;WebhookUrl=https%3A//webhook.site/c32e0033-ee49-40cc-a5ce-18afb610b832;original_service_id=22029;ScreenHeight=864;ScreenWidth=1536;JavaEnabled=False;TimeZoneOffset=-240;Region=ru-RU;ColorDepth=24;UserAgent=Mozilla/5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit/537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome/123.0.0.0%20Safari/537.36;acceptHeader=text/html;javaScriptEnabled=True;Email=dgushch%40gmail.com;IP=212.58.120.107;ReceiptEmail=dgushch%40gmail.com;IsSendReceipt=True",
  "Service_Id": "22029",
  "PaymentMethod": "Card",
  "CardMasked": "533669******3348",
  "ErrorMessage": "Insufficient funds",
  "ExpirationDate": "05/22",
  "RRN": "024845822295",
  "CardHolder": "User Userovich",
  "ErrorCode": "7008",
  "ClientMessage": "Недостаточно средств на карте"
'''

# ошибка оплаты
'''
  "Event": "Fail",
  "Amount": "10.00",
  "Currency": "RUB",
  "DateTime": "09.04.2024 20.30.35",
  "IsTest": 0,
  "Email": "dgushch@gmail.com",
  "Brand": "MASTERCARD",
  "Bank": "SBERBANK OF RUSSIA",
  "CountryCodeAlpha2": "RU",
  "TransactionId": "PS00000418936538",
  "OrderId": "524275902-4000-2",
  "Description": "524275902:3:4000:524275902:415",
  "Service_Id": "22029",
  "PaymentMethod": "Card",
  "CardMasked": "533669******3348",
  "ErrorMessage": "Insufficient funds",
  "ExpirationDate": "05/22",
  "RRN": "024845822295",
  "CardHolder": "User Userovich",
  "ErrorCode": "7008",
  "ClientMessage": "Недостаточно средств на карте"
'''
