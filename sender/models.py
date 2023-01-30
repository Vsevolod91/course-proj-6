from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse_lazy
from django.contrib.auth.models import User


NULLABLE = {'blank': True, 'null': True}


class ConfigMailing(models.Model):
    count = 1

    STATUS_DONE = 'Завершена'
    STATUS_CREATED = 'Создана'
    STATUS_STARTED = 'Запущена'
    STATUSES = (
        (STATUS_DONE, 'Завершена'),
        (STATUS_CREATED, 'Создана'),
        (STATUS_STARTED, 'Запущена')
    )

    PERIOD_DAY = 'Ежедневно'
    PERIOD_WEEK = 'Раз в неделю'
    PERIOD_MONTH = 'Раз в месяц'
    PERIODS = (
        (PERIOD_DAY, 'Ежедневно'),
        (PERIOD_WEEK, 'Раз в неделю'),
        (PERIOD_MONTH, 'Раз в месяц')
    )

    username = models.ForeignKey(User, verbose_name='Логин клиента', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Название рассылки', unique=True, max_length=200)
    hour = models.ForeignKey('Hour', verbose_name='Час рассылки', on_delete=models.PROTECT, default=12)
    minute = models.ForeignKey('Minute', verbose_name='Минуты', default=1, on_delete=models.PROTECT, **NULLABLE)
    periodicity = models.CharField(choices=PERIODS, default=PERIOD_DAY, max_length=20, verbose_name='Периодичность')
    mail_dump = models.FileField(verbose_name='База рассылки в формате .txt', upload_to=f'maildumps/{count}/', **NULLABLE)
    status = models.CharField(choices=STATUSES, default=STATUS_CREATED, max_length=20, verbose_name='Статус')
    weekday = models.ForeignKey('WeekDay', verbose_name='День недели', on_delete=models.PROTECT,  **NULLABLE)
    monthdate = models.ForeignKey('MonthDate', verbose_name='Дата месяца', on_delete=models.PROTECT, **NULLABLE)
    cron_period = models.CharField(verbose_name='Период задачи', max_length=100, **NULLABLE)
    cron_path = models.CharField(verbose_name='Путь задачи', max_length=100, **NULLABLE)

    def __int__(self, *args, **kwargs):
        self.count += 1
        super().__init__(self, *args, **kwargs)

    def __str__(self):
        return f'{self.title}, {self.hour}, {self.minute}, {self.periodicity}, {self.mail_dump}, {self.status}'

    def get_absolute_url(self):
        return reverse_lazy('sender:mailing_detail', kwargs={'pk': self.pk})

    class Meta():
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'


class LetterMailing(models.Model):
    STATUS_SENT = 'Отправлено'
    STATUS_WAIT = 'Ожидает отправки'
    STATUSES = (
        (STATUS_SENT, 'Отправлено'),
        (STATUS_WAIT, 'Ожидает отправки')
    )

    username = models.ForeignKey(User, verbose_name='Логин клиента', on_delete=models.CASCADE)
    mailing = models.ForeignKey('ConfigMailing', verbose_name='Рассылка', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Тема письма', max_length=50, null=False)
    content = models.TextField(verbose_name='Содержание письма', null=False)
    position = models.PositiveIntegerField(verbose_name='Очередь на отправку', **NULLABLE, validators=[MinValueValidator(10), MaxValueValidator(5000000)])
    status = models.CharField(verbose_name='Статус отправки', choices=STATUSES, default=STATUS_WAIT, max_length=20)

    def __lt__(self, other):
        return self.position < other

    def __gt__(self, other):
        return self.position > other

    def __eq__(self, other):
        return self.position == other

    def __ne__(self, other):
        return self.position != other

    def __str__(self):
        return f'{self.id}, {self.title}, {self.content}'

    class Meta():
        verbose_name = 'письмо'
        verbose_name_plural = 'письма'


class TryMailing(models.Model):
    username = models.ForeignKey(User, verbose_name='Логин клиента', on_delete=models.CASCADE)
    mailing = models.OneToOneField('ConfigMailing', verbose_name='Рассылка', **NULLABLE, on_delete=models.CASCADE)
    letter = models.ForeignKey('LetterMailing', verbose_name='Отправленное письмо', **NULLABLE, on_delete=models.CASCADE)
    date_time_try = models.DateTimeField(verbose_name='Дата и время последней попытки', auto_now=True)
    mail_server_respond = models.CharField(verbose_name='Ответ почтового сервера', **NULLABLE, max_length=500)
    count_try = models.SmallIntegerField(verbose_name='Количество попыток', default=0)

    def __str__(self):
        return f'{self.date_time_try}, {self.mail_server_respond}, {self.count_try}'

    class Meta():
        verbose_name = 'попытка'
        verbose_name_plural = 'попытки'


class MonthDate(models.Model):
    number = models.SmallIntegerField(verbose_name='Дата месяца', primary_key=True)

    def __str__(self):
        return f'{self.number}'

    class Meta():
        verbose_name = 'число месяца'
        verbose_name_plural = 'числа месяца'


class WeekDay(models.Model):
    day = models.CharField(verbose_name='День недели', unique=True, max_length=20)
    day_id = models.SmallIntegerField(verbose_name='Идентификатор дня', **NULLABLE)

    def __str__(self):
        return f'{self.day}'

    class Meta():
        verbose_name = 'день недели'
        verbose_name_plural = 'дни недели'


class Hour(models.Model):
    num = models.CharField(verbose_name='Час рассылки', max_length=2, **NULLABLE)

    def __str__(self):
        return f'{self.num}'

    class Meta():
        verbose_name = 'час'
        verbose_name_plural = 'часы'

class Minute(models.Model):
    num = models.CharField(verbose_name='Минуты рассылки', max_length=2)

    def __str__(self):
        return f'{self.num}'

    class Meta():
        verbose_name = 'минута'
        verbose_name_plural = 'минуты'