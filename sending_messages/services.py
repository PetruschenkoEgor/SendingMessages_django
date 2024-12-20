from django.core.mail import send_mail


def send_message_yandex(subject, message, from_email, recipient_list):
    """ Отправка сообщения на яндекс почту """

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
    )
