from django.core.validators import validate_email
from django.forms import BooleanField, ModelForm, forms
from django.core.exceptions import ValidationError
import re
from django import forms
from sending_messages.models import Sender, Message, Recipient, Mailing
from sending_messages.services import parser_input_email_list
from django.utils.translation import gettext_lazy as _


class StyleFormMixin:
    """ Стилизация формы """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fild_name, fild in self.fields.items():
            if isinstance(fild, BooleanField):
                fild.widget.attrs['class'] = 'form-check-input'
            else:
                fild.widget.attrs['class'] = 'form-control form-control-lg'


class SenderForm(StyleFormMixin, ModelForm):
    """ Форма для отправителя """

    class Meta:
        model = Sender
        fields = '__all__'


class MessageForm(StyleFormMixin, ModelForm):
    """ Форма для письма """

    class Meta:
        model = Message
        fields = '__all__'


class RecipientForm(StyleFormMixin, ModelForm):
    """ Форма для получателей """

    class Meta:
        model = Recipient
        fields = '__all__'

    def clean_emails(self):
        """ Проверяет, существует ли email в базе данных """

        email = self.cleaned_data.get('email')
        if Recipient.objects.filter(email=email).exists():
            raise ValidationError(_("Этот email уже существует."))
        return email


    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['email'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['fio'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['comment'].widget.attrs.update({'class': 'form-control'})


# class RecipientListForm(forms.Form):
#     """ Форма для списка получателей """
#     emails = forms.CharField(widget=forms.Textarea, label='Вставьте список получателей в текстовое поле')
#     # class Meta:
#     #     model = Recipient
#     #     fields = ('email',)
#
#     def clean_emails(self):
#         """ Обработка введенных данных """
#         emails = self.cleaned_data.get('emails')
#         if emails:
#             # проверка, что введен именно email
#             email_list = parser_input_email_list(emails)
#             # проверяем есть ли в БД данный email
#             for email in email_list:
#                 if Recipient.objects.filter(email=email).exists():
#                     raise forms.ValidationError(f'Этот {email} уже существует')
#             return email_list

class RecipientListForm(StyleFormMixin, forms.Form):
    """Форма для списка получателей"""

    emails = forms.CharField(
        widget=forms.Textarea,
        label=_('example@mail.ru, example2@mail.ru, example3@mail.ru'),
        required=False
    )

    def clean_emails(self):
        """Обработка введённых данных"""
        raw_emails = self.cleaned_data.get('emails')
        if not raw_emails:
            return []
        emails = parser_input_email_list(raw_emails)
        cleaned_emails = []

        for email in emails:
            email = email.strip()  # Убираем лишние пробелы вокруг email

            # if Recipient.objects.filter(email=email).exists():  # Проверяем, существует ли такой email в базе данных
            #     raise ValidationError(_(f"Адрес {email} уже зарегистрирован."))

            cleaned_emails.append(email)

        return cleaned_emails


class MailingForm(StyleFormMixin, ModelForm):
    """ Форма для рассылки """

    class Meta:
        model = Mailing
        exclude = ('status',)
