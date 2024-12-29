from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """ Модель пользователя """

    username = None
    email = models.EmailField(unique=True, verbose_name='Email')
    phone_number = models.CharField(max_length=15, verbose_name='Телефон', help_text='Введите номер телефона', blank=True, null=True)
    avatar = models.ImageField(upload_to='users/avatars/', verbose_name='Аватар', help_text='Загрузите аватар', blank=True, null=True)
    country = models.CharField(max_length=150, verbose_name='Страна', help_text='Укажите страну', blank=True, null=True)
    token = models.CharField(max_length=100, verbose_name='Token', blank=True, null=True)

    # аутентификация будет по email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
