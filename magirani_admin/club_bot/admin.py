from django.contrib import admin
from unfold.admin import ModelAdmin
from django.utils.html import format_html

import redis

from .models import (
    User,
    Info,
    Payment,
    Admin,
    Statistic,
    ActionJournal,
    AlterPayMethod,
    PaymentPS,
    SaveMessages,
    MailJournal,
    ErrorJournal,
    Funnel,
)


@admin.register(User)
class Veiw_Admin_Table(ModelAdmin):
    list_display = ['user_id', 'full_name', 'username',  'status', 'kick_date', 'last_payment_datetime',
                    'recurrent', 'tariff', 'email']
    search_fields = ['user', 'username', 'email']
    list_filter = ('status',)

    def last_payment_datetime(self, odj):
        last_payment = Payment.objects.filter(tg_payment_id=odj.last_pay_id)
        result = last_payment.first ()
        if result:
            return result.date
        else:
            return None
    last_payment_datetime.short_description = 'Последняя оплата'


@admin.register(Info)
class Veiw_Admin_Table(ModelAdmin):
    list_display = ['cost_1', 'cost_3', 'cost_6', 'cost_12']


@admin.register(Payment)
class Veiw_Admin_Table(ModelAdmin):
    list_display = ['user_full_name', 'date', 'total_amount', 'tg_payment_id']
    search_fields = ['user_id']

    def user_full_name(self, obj):
        user = User.objects.filter(user_id=obj.user_id).first()

        if not user:
            return 'нет данных'
        full_name = user.full_name.strip () if user.full_name else None
        if full_name:
            return full_name
        else:
            return str(obj.user_id)

    user_full_name.short_description = 'Пользователь'


#    оплата пейселекшон
@admin.register(PaymentPS)
class Veiw_Admin_Table(ModelAdmin):
    list_display = ['user_full_name', 'created_at', 'amount', 'transaction_id', 'recurrent_payment']
    search_fields = ['user_id', 'rebill_id']

    def recurrent_payment(self, obj):
        return 'Да' if obj.recurring_id else 'Нет'

    recurrent_payment.short_description = 'Рекуррент'

    def user_full_name(self, obj):
        user = User.objects.filter(user_id=obj.user_id).first()
        if not user:
            return 'нет данных'
        full_name = user.full_name.strip () if user.full_name else None
        if full_name:
            return full_name
        else:
            return str (obj.user_id)

    user_full_name.short_description = 'Пользователь'


@admin.register(Admin)
class Veiw_Admin_Table(ModelAdmin):
    list_display = ['user_id_str', 'desc', 'only_stat']
    search_fields = ['user_id', 'desc']

    def user_id_str(self, obj):
        return str(obj.user_id)
    user_id_str.short_description = 'ID админа'


@admin.register(Statistic)
class Veiw_Admin_Table(ModelAdmin):
    list_display = ['date', 'all_users', 'new_sub', 'renewed_sub', 'unrenewed_sub', 'per_unrewed_sub', 'per_new_sub', 'save_sub', 'CTL', 'error_rate']
    search_fields = ['date']


@admin.register(ActionJournal)
class Veiw_Admin_Table(admin.ModelAdmin):
    list_display = ['time', 'user_id', 'user_full_name', 'username', 'status', 'action', 'comment']
    search_fields = ['time', 'user_id', 'comment']
    list_filter = ('action', 'status')

    def user_full_name(self, obj):
        user = User.objects.filter(user_id=obj.user_id).first()
        if not user:
            return 'нет данных'
        full_name = user.full_name.strip () if user.full_name else None
        if full_name:
            return full_name
        else:
            return str (obj.user_id)

    def username(self, obj):
        user = User.objects.filter(user_id=obj.user_id).first()
        if not user:
            return None
        elif user.username:
            return user.username
        else:
            return '-'

    username.short_description = 'Юзернейм'
    user_full_name.short_description = 'Пользователь'


@admin.register(AlterPayMethod)
class Veiw_Admin_Table(ModelAdmin):
    list_display = ['orm_id', 'name', 'is_active']


@admin.register(SaveMessages)
class SaveMessagesAdmin(ModelAdmin):
    list_display = ('title',)
    readonly_fields = ('entities',)
    search_fields = ('title', 'text')
    ordering = ('-id',)


@admin.register(MailJournal)
class MailJournalAdmin(ModelAdmin):
    list_display = ('created_at', 'all_msg', 'success', 'failed', 'blocked', 'unblocked', 'time_mailing')
    readonly_fields = ('id', 'created_at', 'all_msg', 'success', 'failed', 'blocked', 'unblocked', 'time_mailing', 'report')
    ordering = ('-id',)

    def has_add_permission(self, request):
        """Запрещаем добавление новых записей из админки"""
        return False


@admin.register(ErrorJournal)
class ErrorJournalAdmin(ModelAdmin):
    list_display = ('created_at', 'user_id', 'error', 'message', 'comment')
    readonly_fields = ('id', 'created_at', 'user_id', 'error', 'message')
    # readonly_fields = ('id', 'created_at', 'error', 'message')
    list_editable = ('comment',)
    ordering = ('-id',)

    def has_add_permission(self, request):
        """Запрещаем добавление новых записей из админки"""
        return False

    def user_full_name(self, obj):
        user = User.objects.filter(user_id=obj.user_id).first()
        if not user:
            return '-'
        full_name = user.full_name.strip() if user.full_name else None
        if full_name:
            return full_name
        else:
            return str(obj.user_id)

    user_full_name.short_description = 'Пользователь'


@admin.register(Funnel)
class FunnelAdmin(ModelAdmin):
    list_display = ('user_full_name', 'next_start_date', 'next_start_time', 'is_active')
    list_filter = ('is_active', 'next_start_date')
    search_fields = ('id', 'group_recip', 'user_id', 'period_id')
    readonly_fields = ('created_at', 'updated_at', 'next_start_date', 'next_start_time', 'period_day')

    fieldsets = (
        (None, {
            'fields': ('next_start_date', 'next_start_time', 'period_day', 'group_recip', 'is_active')
        }),
        ('Дополнительные настройки', {
            'classes': ('collapse',),
            'fields': ('save_msg', 'user_id', 'period_id')
        }),
    )

    def user_full_name(self, obj):
        user = User.objects.filter(user_id=obj.user_id).first()
        if not user:
            return '-'
        full_name = user.full_name.strip() if user.full_name else None
        if full_name:
            return full_name
        else:
            return str(obj.user_id)

    user_full_name.short_description = 'Пользователь'
