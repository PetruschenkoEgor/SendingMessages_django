import re
import logging

from django.core.cache import cache
from django.core.mail import send_mail

from config.settings import CACHE_ENABLED
from sending_messages.models import Recipient, Message, Mailing, AttemptMailing

logger = logging.getLogger(__name__)


def send_message_yandex(subject, message, from_email, recipient_list):
    """ Отправка сообщения на яндекс почту """

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
    )


def parser_input_email_list(emails):
    """ Проверяет введенные emails и преобразует их в список """

    # убираем пробелы и делаем из строки список
    email_list = (emails.replace(' ', '')).split(',')
    # проверяем, что это действительно email
    email_validate_pattern = r'^\S+@\S+\.\S+$'
    email_list_validate = []
    for email in email_list:
        email_validate = re.findall(email_validate_pattern, email)
        email_list_validate += email_validate
    return email_list_validate


def get_recipients_from_cache():
    """ Получаем получателей рассылки из кэша, если кэш пуст, получаем данные из бд """

    if not CACHE_ENABLED:
        logger.info('Кэширование отключено. Данные берутся из БД.')
        return Recipient.objects.all()

    key = 'recipient_list'
    recipients = cache.get(key)
    if recipients is None:
        logger.info('Ошибка кэширования. Данные берутся из БД.')
        recipients = Recipient.objects.all()  # Преобразуем QuerySet в список для кэширования
        cache.set(key, recipients, timeout=60*15)  # Устанавливаем тайм-аут
    else:
        logger.info('Получение данных из кэша.')

    return recipients


def get_recipients_for_owner_from_cache(owner_id):
    """ Получаем получателей рассылки из кэша для конкретного владельца, если кэш пуст, получаем данные из бд """

    if not CACHE_ENABLED:
        logger.info('Кэширование отключено. Данные берутся из БД.')
        return Recipient.objects.filter(owner_id=owner_id)

    key = f'recipient_list_{owner_id}'
    recipients = cache.get(key)
    if recipients is None:
        logger.info('Ошибка кэширования. Данные берутся из БД.')
        recipients = Recipient.objects.filter(owner_id=owner_id)
        cache.set(key, recipients, timeout=60*15)
    else:
        logger.info('Получение данных из кэша.')

    return recipients


def get_messages_from_cache():
    """ Получаем письма из кэша, если кэш пуст, получаем данные из бд """

    if not CACHE_ENABLED:
        logger.info('Кэширование отключено. Данные берутся из БД.')
        return Message.objects.all()

    key = 'message_list'
    messages = cache.get(key)
    if messages is None:
        logger.info('Ошибка кэширования. Данные берутся из БД.')
        messages = Message.objects.all()
        cache.set(key, messages, timeout=60*15)
    else:
        logger.info('Получение данных из кэша.')

    return messages


def get_messages_for_owner_from_cache(owner_id):
    """ Получаем письма из кэша для конкретного владельца, если кэш пуст, получаем данные из бд """

    if not CACHE_ENABLED:
        logger.info('Кэширование отключено. Данные берутся из БД.')
        return Message.objects.filter(owner_id=owner_id)

    key = f'message_list_{owner_id}'
    messages = cache.get(key)
    if messages is None:
        logger.info('Ошибка кэширования. Данные берутся из БД.')
        messages = Message.objects.filter(owner_id=owner_id)
        cache.set(key, messages, timeout=60*15)
    else:
        logger.info('Получение данных из кэша.')

    return messages


def get_mailings_from_cache():
    """ Получаем рассылки из кэша, если кэш пуст, получаем данные из бд """

    if not CACHE_ENABLED:
        logger.info('Кэширование отключено. Данные берутся из БД.')
        return Mailing.objects.all()

    key = 'mailing_list'
    mailings = cache.get(key)
    if mailings is None:
        logger.info('Ошибка кэширования. Данные берутся из БД.')
        mailings = Mailing.objects.all()
        cache.set(key, mailings, timeout=60*15)
    else:
        logger.info('Получение данных из кэша.')

    return mailings


def get_mailings_for_owner_from_cache(owner_id):
    """ Получаем рассылки из кэша для конкретного владельца, если кэш пуст, получаем данные из бд """

    if not CACHE_ENABLED:
        logger.info('Кэширование отключено. Данные берутся из БД.')
        return Mailing.objects.filter(owner_id=owner_id)

    key = f'mailing_list_{owner_id}'
    mailings = cache.get(key)
    if mailings is None:
        logger.info('Ошибка кэширования. Данные берутся из БД.')
        mailings = Mailing.objects.filter(owner_id=owner_id)
        cache.set(key, mailings, timeout=60*15)
    else:
        logger.info('Получение данных из кэша.')

    return mailings


def get_mailings_active_from_cache():
    """ Получаем активные рассылки из кэша, если кэш пуст, получаем данные из бд """

    if not CACHE_ENABLED:
        logger.info('Кэширование отключено. Данные берутся из БД.')
        return Mailing.objects.filter(status='Запущена')

    key = 'mailing_active_list'
    mailings = cache.get(key)
    if mailings is None:
        logger.info('Ошибка кэширования. Данные берутся из БД.')
        mailings = Mailing.objects.filter(status='Запущена')
        cache.set(key, mailings, timeout=60 * 15)
    else:
        logger.info('Получение данных из кэша.')

    return mailings


def get_mailings_active_for_owner_from_cache(owner_id):
    """ Получаем активные рассылки из кэша для конкретного владельца, если кэш пуст, получаем данные из бд """

    if not CACHE_ENABLED:
        logger.info('Кэширование отключено. Данные берутся из БД.')
        return Mailing.objects.filter(status='Запущена', owner_id=owner_id)

    key = f'mailing_active_list_{owner_id}'
    mailings = cache.get(key)
    if mailings is None:
        logger.info('Ошибка кэширования. Данные берутся из БД.')
        mailings = Mailing.objects.filter(status='Запущена', owner_id=owner_id)
        cache.set(key, mailings, timeout=60 * 15)
    else:
        logger.info('Получение данных из кэша.')

    return mailings


def get_attempt_mailings_for_owner_from_cache(owner_id):
    """ Получаем попытки рассылки из кэша для конкретного владельца, если кэш пуст, получаем данные из бд """

    if not CACHE_ENABLED:
        logger.info('Кэширование отключено. Данные берутся из БД.')
        return AttemptMailing.objects.filter(owner_id=owner_id)

    key = 'attempt_mailing_list'
    attempt_mailing = cache.get(key)
    if attempt_mailing is None:
        logger.info('Ошибка кэширования. Данные берутся из БД.')
        attempt_mailing = AttemptMailing.objects.filter(owner_id=owner_id)
        cache.set(key, attempt_mailing, timeout=60*15)
    else:
        logger.info('Получение данных из кэша.')

    return attempt_mailing
