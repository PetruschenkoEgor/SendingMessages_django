from django.forms import BooleanField, ModelForm

from sending_messages.models import Sender, Message, Recipient


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
