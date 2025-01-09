from django import forms
from django.core.exceptions import ValidationError
from django.forms import BooleanField, ModelForm
from django.utils.translation import gettext_lazy as _

from sending_messages.models import Mailing, Message, Recipient
from sending_messages.services import parser_input_email_list


class StyleFormMixin:
    """Стилизация формы"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fild_name, fild in self.fields.items():
            if isinstance(fild, BooleanField):
                fild.widget.attrs["class"] = "form-check-input"
            else:
                fild.widget.attrs["class"] = "form-control form-control-lg"


class MessageForm(StyleFormMixin, ModelForm):
    """Форма для письма"""

    class Meta:
        model = Message
        fields = ("topic", "body")


class RecipientForm(StyleFormMixin, ModelForm):
    """Форма для получателей"""

    class Meta:
        model = Recipient
        fields = (
            "email",
            "fio",
            "comment",
            "active",
        )

    def clean_emails(self):
        """Проверяет, существует ли email в базе данных"""

        email = self.cleaned_data.get("email")
        if Recipient.objects.filter(email=email).exists():
            raise ValidationError(_("Этот email уже существует."))
        return email


class RecipientListForm(StyleFormMixin, forms.Form):
    """Форма для списка получателей"""

    emails = forms.CharField(
        widget=forms.Textarea, label=_("example@mail.ru, example2@mail.ru, example3@mail.ru"), required=False
    )

    def clean_emails(self):
        """Обработка введённых данных"""
        raw_emails = self.cleaned_data.get("emails")
        if not raw_emails:
            return []
        emails = parser_input_email_list(raw_emails)
        cleaned_emails = []

        for email in emails:
            email = email.strip()  # Убираем лишние пробелы вокруг email

            cleaned_emails.append(email)

        return cleaned_emails


class MailingForm(StyleFormMixin, ModelForm):
    """Форма для рассылки"""

    class Meta:
        model = Mailing
        exclude = ("status", "owner")

    def __init__(self, *args, **kwargs):
        """При создании рассылки, пользователь может выбрать только свои сообщения и получателей"""

        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["message"].queryset = Message.objects.filter(owner=user)
            self.fields["recipients"].queryset = Recipient.objects.filter(owner=user)
