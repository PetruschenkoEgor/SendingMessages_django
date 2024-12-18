from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, DetailView

from sending_messages.forms import SenderForm, MessageForm, RecipientForm
from sending_messages.models import Mailing, Sender, Message, Recipient


class MailingTemplateView(TemplateView):
    """ Главная страница """

    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        """ Передача объекта Mailing в шаблон """

        context = super().get_context_data()
        context['mailings'] = Mailing.objects.count()
        context['mailings_activ'] = Mailing.objects.filter(status='Запущена').count()
        return context


class SenderCreateView(CreateView):
    """ Создание рассылки - отправитель(1) """

    model = Sender
    form_class = SenderForm
    template_name = 'mailing1.html'


class MessageCreateView(CreateView):
    """ Создание рассылки - письмо(2) """

    model = Message
    form_class = MessageForm
    template_name = 'mailing2.html'


class RecipientCreateView(CreateView):
    """ Создание рассылки - получатели(3) """

    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing3.html'


class SendingDetailView(DetailView):
    """ Создание рассылки - отправка(4) """

    model = Mailing
    template_name = 'mailing4.html'
    context_object_name = 'mailing'

    def get_context_data(self, **kwargs):
        """ Из модели рассылки получаем отправителя, письмо и получателей и передаем в шаблон """
        context = super().get_context_data(**kwargs)
        mailing = self.get_object()
        context['sender'] = mailing.sender
        context['message'] = mailing.message
        context['recipients'] = mailing.recipients.all()
        return context
