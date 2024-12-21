from django.db import models


class Recipient(models.Model):
    """ Получатель рассылки """
    email = models.EmailField(verbose_name='Email получателя', help_text='Введите Email', unique=True)
    fio = models.CharField(max_length=300, verbose_name='Ф.И.О.', help_text='Введите фамилию, имя, отчество', blank=True, null=True)
    comment = models.TextField(verbose_name='Комментарий', help_text='Введите комментарий', blank=True, null=True)
    active = models.BooleanField(verbose_name='Активность', help_text='Укажите активность', default=True)

    class Meta:
        verbose_name = 'Получатель рассылки'
        verbose_name_plural = 'Получатели рассылки'
        ordering = ['fio',]

    def __str__(self):
        return f'{self.email}'


class Message(models.Model):
    """ Сообщение """
    topic = models.CharField(max_length=250, verbose_name='Тема письма', help_text='Введите тему письма')
    body = models.TextField(verbose_name='Текст письма', help_text='Введите текст письма')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return self.topic


class Sender(models.Model):
    """ Отправитель """
    name = models.CharField(max_length=250, verbose_name='Имя отправителя', help_text='Введите имя отправителя', blank=True, null=True)
    email = models.EmailField(verbose_name='Email отправителя', help_text='Введите email отправителя', unique=True)
    organization = models.CharField(max_length=300, verbose_name='Организация', help_text='Введите название организации', blank=True, null=True)

    class Meta:
        verbose_name = 'Отправитель'
        verbose_name_plural = 'Отправители'
        ordering = ['name',]

    def __str__(self):
        return self.email


class Mailing(models.Model):
    """ Рассылка """
    STATUS_CHOICES = [
        ('Завершена', 'завершена'),
        ('Создана', 'создана'),
        ('Запущена', 'запущена'),
    ]

    date_time_first_shipment = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время первой отправки')
    date_time_end_shipment = models.DateTimeField(auto_now=True, verbose_name='Дата и время окончания отправки')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Создана', verbose_name='Статус')
    message = models.ForeignKey('Message', on_delete=models.SET_NULL, verbose_name='Сообщение', help_text='Введите сообщение', blank=True, null=True, related_name='mailings')
    recipients = models.ManyToManyField(Recipient, verbose_name='Получатель', help_text='Укажите получателя', blank=True, null=True)
    sender = models.ForeignKey('Sender', on_delete=models.SET_NULL, verbose_name='Отправитель', help_text='Укажите отправителя', blank=True, null=True, related_name='mailings')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['date_time_first_shipment', 'status',]

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
    sending_count = models.PositiveIntegerField(verbose_name='Счетчик рассылок', default=0)

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылки'
        ordering = ['date_time_attempt', 'status',]

    def __str__(self):
        return f'{self.date_time_attempt} - {self.status}'
