import enum


class Action(str, enum.Enum):
    SAVE = 'save'
    FUNNEL = 'funnel'
    DEL = 'del'


class UserStatus(str, enum.Enum):
    NEW = 'new'
    SUB = 'sub'
    NOT_SUB = 'not_sub'
    REFUND = 'refund'
    BAN = 'ban'


class FunnelAction(str, enum.Enum):
    ACTIVE = 'active'
    PERIOD = 'period'
    TIME = 'time'
    DEL = 'del'


class Unit(str, enum.Enum):
    DAYS = 'days'
    MOUNTS = 'mounts'
