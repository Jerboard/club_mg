from enum import Enum


class UserStatus(str, Enum):
    NEW = 'new'
    SUB = 'sub'
    NOT_SUB = 'not_sub'
    BAN = 'ban'
    REFUND = 'refund'


class RecurrentStatus(str, Enum):
    NEW = 'new'
    ACTIVE = 'active'
    OVERDUE = 'overdue'
    TERMINATED = 'terminated'


class PaymentStatus(str, Enum):
    SUCCESSFULLY = 'successfully'
    FAILED = 'failed'


class BaseCB(str, Enum):
    BACK_COM_START = 'back_com_start'
    CLOSE = 'close'
