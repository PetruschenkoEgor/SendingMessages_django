import logging

from django.core.cache import cache
from config.settings import CACHE_ENABLED
from users.models import User


logger = logging.getLogger(__name__)


def get_users_from_cache():
    """ Получаем пользователей из кэша, если кэш пуст, получаем данные из бд """

    if CACHE_ENABLED:
        logger.info('Кэширование отключено. Данные берутся из БД.')
        return User.objects.all()

    key = 'user_list'
    users = cache.get(key)
    if users is None:
        logger.info('Ошибка кэширования. Данные берутся из БД.')
        users = User.objects.all()
        cache.set(key, users, timeout=60*15)
    else:
        logger.info('Получение данных из кэша.')

    return users
