from django.conf import settings
from django.db import models


class Recipient(models.Model):
    """ Получатель рассылки """
    # убрал уникальность, потому что другие пользователи не могут добавить себе такого же получателя
    email = models.EmailField(verbose_name='Email получателя', help_text='Введите Email')
    fio = models.CharField(max_length=300, verbose_name='Ф.И.О.', help_text='Введите фамилию, имя, отчество', blank=True, null=True)
    comment = models.TextField(verbose_name='Комментарий', help_text='Введите комментарий', blank=True, null=True)
    active = models.BooleanField(verbose_name='Активность', help_text='Укажите активность', default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Владелец получателя', help_text='Укажите владельца', blank=True, null=True, related_name='recipients')

    class Meta:
        verbose_name = 'Получатель рассылки'
        verbose_name_plural = 'Получатели рассылки'
        ordering = ['fio',]
        permissions = [
            ('can_view_all_recipients', 'Can view recipients'),
        ]

    def __str__(self):
        return f'{self.email}'


class Message(models.Model):
    """ Сообщение """
    topic = models.CharField(max_length=250, verbose_name='Тема письма', help_text='Введите тему письма')
    body = models.TextField(verbose_name='Текст письма', help_text='Введите текст письма')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Владелец сообщения',
                              help_text='Укажите владельца', blank=True, null=True, related_name='messages')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        permissions = [
            ('can_view_all_messages', 'Can view all messages'),
        ]

    def __str__(self):
        return self.topic


class Mailing(models.Model):
    """ Рассылка """
    STATUS_CHOICES = [
        ('Завершена', 'завершена'),
        ('Создана', 'создана'),
        ('Запущена', 'запущена'),
    ]

    name = models.CharField(max_length=150, verbose_name='Название рассылки', help_text='Введите название рассылки', blank=True, null=True)
    date_time_first_shipment = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время первой отправки')
    date_time_end_shipment = models.DateTimeField(auto_now=True, verbose_name='Дата и время окончания отправки')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Создана', verbose_name='Статус')
    message = models.ForeignKey('Message', on_delete=models.SET_NULL, verbose_name='Сообщение', help_text='Введите сообщение', blank=True, null=True, related_name='mailings')
    recipients = models.ManyToManyField(Recipient, verbose_name='Получатель', help_text='Укажите получателя', blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Владелец рассылки', help_text='Укажите владельца', blank=True, null=True, related_name='mailings')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['date_time_first_shipment', 'status',]
        permissions = [
            ('can_view_all_mailings', 'Can view all mailings'),
            ('can_disabling_mailing', 'Can disabling mailing')
        ]

    def __str__(self):
        return f'{self.date_time_first_shipment} - {self.status}'


class AttemptMailing(models.Model):
    """ Попытка рассылки """
    STATUS_CHOICES = [
        ('Успешно', 'успешно'),
        ('Не успешно', 'не успешно'),
    ]

    date_time_attempt = models.DateTimeField(auto_now=True, verbose_name='Дата и время попытки')
    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default='Не успешно', verbose_name='Статус')
    mail_server_response = models.TextField(verbose_name='Ответ почтового сервера')
    mailing = models.ForeignKey('Mailing', on_delete=models.CASCADE, verbose_name='Рассылка', help_text='Введите рассылку', related_name='attemptmailings')
    sending_count_ok = models.PositiveIntegerField(verbose_name='Счетчик успешных рассылок', default=0)
    sending_count_error = models.PositiveIntegerField(verbose_name='Счетчик неуспешных рассылок', default=0)
    count_messages = models.PositiveIntegerField(verbose_name='Счетчик отправленных сообщений', default=0)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Владелец попытки рассылки',
                              help_text='Укажите владельца', blank=True, null=True, related_name='attemptmailings')

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылки'
        ordering = ['date_time_attempt', 'status',]

    def __str__(self):
        return f'{self.date_time_attempt} - {self.status}'
