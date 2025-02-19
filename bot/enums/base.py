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


class JobName(str, enum.Enum):
    CHECK_SUB = 'check_sub'
    ADD_STATISTIC = 'add_statistic_history'
    CHECK_PAY_YOO = 'check_pay_yoo'


job_name_list = [
    JobName.CHECK_SUB.value,
    JobName.ADD_STATISTIC.value,
    JobName.CHECK_PAY_YOO.value,
]