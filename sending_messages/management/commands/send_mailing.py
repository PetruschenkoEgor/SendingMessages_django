from django.conf import settings
from django.core.mail import send_mail
from django.core.management import BaseCommand

from sending_messages.models import Message, Recipient


class Command(BaseCommand):
    """ Отправка рассылки через командную строку(последнее сообщение) """

    def handle(self, *args, **options):
        # последнее сообщение по дате создания
        message_last = Message.objects.last()
        subject = message_last.topic
        message = message_last.body
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [recipient.email for recipient in Recipient.objects.filter(active=True)]

        send_mail(subject, message, from_email, recipient_list)
        self.stdout.write(self.style.SUCCESS('Отправлено успешно'))
