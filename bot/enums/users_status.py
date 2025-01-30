import enum


class BaseStatus(str, enum.Enum):
    SEND_EMAIL = 'send_email'
    ALT_PAY_EMAIL = 'alt_pay_email'
    ADD_USER_EMAIL = 'add_user_email'
    SEND_USERS_MESSAGE = 'send_users_message'
    DEL_USER = 'del_user'
