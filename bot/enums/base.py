import enum


class UserStatus(str, enum.Enum):
    NEW = 'new'
    SUB = 'sub'
    NOT_SUB = 'not_sub'
    REFUND = 'refund'
    BAN = 'ban'
