import enum


class BaseCB(str, enum.Enum):
    BACK_COM_START = 'back_com_start'
    CLOSE = 'close'


class AdminCB(str, enum.Enum):
    BACK_ADMIN_START = 'back_admin_start'
    SAVE_MESSAGES_1 = 'save_messages_1'
    SAVE_MESSAGES_2 = 'save_messages_2'
    DEL_MESSAGE_1 = 'del_message_1'
    ADD_MONTHS_1 = 'add_months_1'
    ADD_MONTHS_2 = 'add_months_2'
    DEL_USER_1 = 'del_user_1'
    SEND_MESSAGES_1 = 'send_messages_1'
    SEND_MESSAGES_2 = 'send_messages_2'
    SEND_MESSAGES_3 = 'send_messages_3'
    SEND_MESSAGES_4 = 'send_messages_4'
    SEND_MESSAGES_5 = 'send_messages_5'
    SEND_MESSAGES_6 = 'send_messages_6'
    SEND_MESSAGES_7 = 'send_messages_7'
    SEND_MESSAGES_8 = 'send_messages_8'


class UserCB(str, enum.Enum):
    PAY_YOOKASSA_0 = 'pay_yookassa_0'
    PAY_YOOKASSA_1 = 'pay_yookassa_1'
    PAY_YOOKASSA_2 = 'pay_yookassa_2'
    SUPPORT_0 = 'support_0'
    SUPPORT_1 = 'support_1'
    MY_ACCOUNT = 'my_account'
    UNSUBSCRIBE = 'unsubscribe'


class FunnelCB(str, enum.Enum):
    MENU = 'funnel_menu'
    CREATE = 'funnel_create'
    VIEW = 'funnel_view'
    EDIT = 'funnel_edit'
    SEND = 'funnel_send'

