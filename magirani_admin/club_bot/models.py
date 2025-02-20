from django.db import models

from .data import users_status


class User(models.Model):
    id = models.AutoField (primary_key=True)
    user_id = models.BigIntegerField('№ тг', null=True, blank=True, default=11111, unique=False)
    full_name = models.CharField('Пользователь', max_length=255, null=True, blank=True)
    username = models.CharField('Юзернейм', max_length=50, null=True, blank=True)
    first_visit = models.DateField('Дата первого визита', null=True, blank=True)
    status = models.CharField('Статус', max_length=30, null=True, blank=True, choices=users_status)
    kick_date = models.DateField('Оплачен до', null=True, blank=True)
    alarm_2_day = models.BooleanField('Предупреждение', null=True, blank=True, default=False)
    last_pay_id = models.CharField('Последняя транзакция', max_length=100, null=True, blank=True)
    recurrent = models.BooleanField('Подписка', null=True, blank=True, default=False)
    tariff = models.CharField('Тариф', max_length=30, null=True, blank=True)
    email = models.CharField('Почта', max_length=100, null=True, blank=True)
    is_blocked = models.BooleanField('Блокировали бот', null=True, blank=True, default=False)

    def __str__(self):
       # return self.full_name if self.full_name else '-'
       return f'{self.full_name}' if self.full_name else f'{self.user_id}'

    class Meta:
        verbose_name = 'Подписчик Magirani'
        verbose_name_plural = 'Подписчики Magirani'
        db_table = 'users'
        managed = False


class Info(models.Model):
    id = models.AutoField (primary_key=True)
    cost_1 = models.IntegerField('1 месяц', null=True, blank=True)
    cost_3 = models.IntegerField('3 месяца', null=True, blank=True)
    cost_6 = models.IntegerField('6 месяцев', null=True, blank=True)
    cost_12 = models.IntegerField('12 месяцев', null=True, blank=True)

    def __int__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Стоимость подписки'
        verbose_name_plural = 'Стоимость подписок'
        db_table = 'info'
        managed = False


class Payment(models.Model):
    id = models.AutoField (primary_key=True)
    user_id = models.BigIntegerField('№ тг', null=True, blank=True)
    date = models.DateTimeField('Время', null=True, blank=True)
    total_amount = models.IntegerField('Сумма', null=True, blank=True, default=None)
    tg_payment_id = models.CharField('ID платежа', max_length=100,  null=True, blank=True)
    # provider_payment_charge_id = models.CharField('?????', max_length=100, null=True, blank=True)


    def __str__(self):
        return str(self.user_id)

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
        db_table = 'payments'
        managed = False


class Admin(models.Model):
    id = models.AutoField (primary_key=True)
    user_id = models.BigIntegerField('ID админа')
    desc = models.CharField('Примечание', max_length=255, null=True, blank=True)
    only_stat = models.BooleanField('Только статистика', null=True, blank=True)

    def __str__(self):
        return str(self.user_id)

    class Meta:
        verbose_name = 'Админ'
        verbose_name_plural = 'Админы'
        db_table = 'admin'
        managed = False


class Statistic(models.Model):
    id = models.AutoField (primary_key=True)
    date = models.DateField('Дата', null=True, blank=True)
    all_users = models.IntegerField('Всего пользователей', null=True, blank=True)
    new_sub = models.IntegerField('Новых пользователей', null=True, blank=True, default=None)
    renewed_sub = models.IntegerField('Продлило подписку', null=True, blank=True)
    unrenewed_sub = models.IntegerField('Отписалось', null=True, blank=True)
    per_unrewed_sub = models.FloatField('% отписок', null=True, blank=True)
    per_new_sub = models.FloatField('% новых подписок', null=True, blank=True)
    save_sub = models.FloatField('Удержание', null=True, blank=True)
    CTL = models.FloatField('Продолжительность жизни', null=True, blank=True)
    error_rate = models.FloatField('Погрешность', null=True, blank=True)

    def __str__(self):
        return str(self.date)

    class Meta:
        verbose_name = 'Статистика'
        verbose_name_plural = 'Статистика'
        db_table = 'statistic'
        managed = False


class ActionJournal(models.Model):
    id = models.AutoField (primary_key=True)
    time = models.DateTimeField('Время', null=True, blank=True)
    user_id = models.BigIntegerField('ID пользователя', null=True, blank=True)
    status = models.CharField('Статус', max_length=100, null=True, blank=True)
    action = models.CharField('Действие', max_length=100, null=True, blank=True)
    comment = models.TextField('Комментарий', max_length=100, null=True, blank=True)

    def __str__(self):
        return self.action

    class Meta:
        verbose_name = 'Журнал'
        verbose_name_plural = 'Журнал'
        db_table = 'action_journal'
        managed = False


class AlterPayMethod(models.Model):
    id = models.AutoField (primary_key=True)
    orm_id = models.IntegerField('ID в системе', null=True, blank=True, default=0)
    name = models.CharField('Название', max_length=255, null=True, blank=True)
    is_active = models.BooleanField('Активен', max_length=100, null=True, blank=True, default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Альтернативный способ оплаты'
        verbose_name_plural = 'Альтернативные способы оплаты'
        db_table = 'alter_pay_method'
        managed = False


class PaymentPS(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    order_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, default='new', null=True, blank=True)
    # pay_id = models.CharField(max_length=255)
    rebill_id = models.CharField(max_length=255, null=True, blank=True)
    recurring_id = models.CharField(max_length=255, null=True, blank=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    pay_link = models.CharField(max_length=255, null=True, blank=True)
    card_type = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.order_id

    class Meta:
        verbose_name = 'Оплата PS'
        verbose_name_plural = 'Оплаты PS'
        db_table = 'payments_ps'
        managed = False


class PhotosTable(models.Model):
    id = models.AutoField (primary_key=True)
    photo_id = models.CharField('ID фото', max_length=255, null=True, blank=True)

    def __str__(self):
        return f'id: {self.photo_id}'

    class Meta:
        verbose_name = 'Фото'
        verbose_name_plural = 'Фото'
        db_table = 'photos'
        managed = False


class SaveMessages(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    text = models.TextField()
    entities = models.TextField()
    photo = models.CharField(max_length=255, blank=True, null=True)
    # group_recip = models.CharField(max_length=255, blank=True, null=True)
    # period_id = models.IntegerField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Сохранённое сообщение'
        verbose_name_plural = 'Сохранённые сообщения'
        db_table = 'save_messages'
        managed = False


class MailJournal(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    all_msg = models.IntegerField(verbose_name="Всего сообщений")
    success = models.IntegerField(verbose_name="Успешно")
    failed = models.IntegerField(verbose_name="Ошибок")
    blocked = models.IntegerField(verbose_name="Блокировали бот")
    unblocked = models.IntegerField(verbose_name="Разблокировали бот")
    time_mailing = models.DurationField(verbose_name="Время рассылки")
    report = models.TextField(verbose_name="Отчёт")

    class Meta:
        db_table = 'mailing_journal'
        verbose_name = "Журнал рассылки"
        verbose_name_plural = "Журналы рассылок"
        managed = False

    def __str__(self):
        return f"Журнал {self.id} - {self.created_at}"


class ErrorJournal(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    user_id = models.IntegerField(verbose_name="ID пользователя")
    error = models.CharField(max_length=255, verbose_name="Ошибка")
    message = models.TextField(verbose_name="Сообщение")
    comment = models.CharField(max_length=255, verbose_name="Комментарий", null=True, blank=True)

    class Meta:
        db_table = 'error_journal'
        verbose_name = "Журнал ошибок"
        verbose_name_plural = "Журналы ошибок"
        managed = False

    def __str__(self):
        return f"Ошибка {self.id} - {self.created_at}"


class Funnel(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    next_start_date = models.DateField(null=True, blank=True, verbose_name="Дата следующего старта")
    next_start_time = models.TimeField(null=True, blank=True, verbose_name="Время следующего старта")
    # save_msg_id = models.IntegerField(null=True, blank=True, verbose_name="ID сохранённого сообщения")
    save_msg = models.ForeignKey(SaveMessages, on_delete=models.SET_NULL, verbose_name="Сообщение", null=True, blank=True)
    user_id = models.IntegerField(null=True, blank=True, verbose_name="ID пользователя")
    period_day = models.IntegerField(default=0, verbose_name="Периодичность в днях")
    group_recip = models.CharField(max_length=255, verbose_name="Группа получателей")
    period_id = models.IntegerField(null=True, blank=True, verbose_name="ID периода")
    is_active = models.BooleanField(default=False, verbose_name="Активна")

    class Meta:
        verbose_name = "Воронка"
        verbose_name_plural = "Воронки"
        db_table = "funnel"
        managed = False

    def __str__(self):
        return f"Воронка #{self.id}"


# виртуальная модель для просмотра работ в редисе
class RedisJob(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название файла",
    )
    content = models.TextField(verbose_name="Содержимое",)

    class Meta:
        verbose_name = "Конфигурация"
        verbose_name_plural = "Конфигурации"
        managed = False

    def save(self, *args, **kwargs):
        return
