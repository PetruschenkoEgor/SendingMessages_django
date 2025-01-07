from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

from sending_messages.models import Recipient, Message, Mailing


class Command(BaseCommand):
    """ Создание группы 'Менеджеры' """

    def handle(self, *args, **options):
        # проверка существования группы
        group, created = Group.objects.get_or_create(name='Менеджеры')
        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" была успешно создана'))
        else:
            self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" уже существует'))

        # получение права для модели Recipient
        content_type_recipient = ContentType.objects.get_for_model(Recipient)
        permission_recipient = Permission.objects.get(
            codename='can_view_all_recipients',
            content_type=content_type_recipient
        )

        # получение права для модели Message
        content_type_message = ContentType.objects.get_for_model(Message)
        permission_message = Permission.objects.get(
            codename='can_view_all_messages',
            content_type=content_type_message
        )

        # получение права для модели Mailing
        content_type_mailing = ContentType.objects.get_for_model(Mailing)
        permission_mailing_view = Permission.objects.get(
            codename='can_view_all_mailings',
            content_type=content_type_mailing
        )
        permission_mailing_disable = Permission.objects.get(
            codename='can_disabling_mailing',
            content_type=content_type_mailing
        )

        # добавление права к группе
        group.permissions.add(permission_recipient, permission_message, permission_mailing_view, permission_mailing_disable)
        self.stdout.write(self.style.SUCCESS('Права добавлены группе "Менеджеры"'))
