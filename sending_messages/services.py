import re

from django.core.mail import send_mail


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
    email_validate_pattern = r"^\S+@\S+\.\S+$"
    email_list_validate = []
    for email in email_list:
        email_validate = re.findall(email_validate_pattern, email)
        email_list_validate += email_validate
    return email_list_validate
