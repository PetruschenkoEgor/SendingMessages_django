from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, DetailView, ListView

from sending_messages.forms import SenderForm, MessageForm, RecipientForm, MailingForm
from sending_messages.models import Mailing, Sender, Message, Recipient, AttemptMailing


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
    success_url = reverse_lazy('sending_messages:add_message')

    def form_valid(self, form):
        """ Сохраняет объект в БД и записывает его ид в сессии """
        # сохраняет объект в БД и возвращает http ответ
        sender = super().form_valid(form)
        # сохраняет ид созданного объекта в сессии для использования на следующем этапе
        self.request.session['sender_id'] = self.object.id
        return sender


class MessageCreateView(CreateView):
    """ Создание рассылки - письмо(2) """

    model = Message
    form_class = MessageForm
    template_name = 'mailing2.html'
    success_url = reverse_lazy('sending_messages:add_recipient')

    def form_valid(self, form):
        """ Сохраняет объект в БД и записывает его ид в сессии """
        # сохраняет объект в БД и возвращает http ответ
        message = super().form_valid(form)
        # сохраняет ид созданного объекта в сессии для использования на следующем этапе
        self.request.session['message_id'] = self.object.id
        return message


class RecipientCreateView(CreateView):
    """ Создание рассылки - получатели(3) """

    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing3.html'
    success_url = reverse_lazy('sending_messages:sending')

    def form_valid(self, form):
        """ Сохраняет объект в БД и записывает его ид в сессии """
        # сохраняет объект в БД и возвращает http ответ
        recipient = super().form_valid(form)
        # создаем список с идентификаторами получателей и добавляем в него иды
        recipient_ids = self.request.session.get('recipient_ids', [])
        recipient_ids.append(self.object.id)
        # сохраняет ид созданного объекта в сессии для использования на следующем этапе
        self.request.session['recipient_ids'] = recipient_ids
        return recipient


class SendingCreateView(CreateView):
    """ Создание рассылки - отправка(4) """

    model = Mailing
    form_class = MailingForm
    template_name = 'mailing4.html'

    def form_valid(self, form):
        # получаем сохраненные идентификаторы
        sender_id = self.request.session.get('sender_id')
        message_id = self.request.session.get('message_id')
        # получаем список ид получателей
        recipient_ids = self.request.session.get('recipient_ids', [])
        print(f'количество1: {len(recipient_ids)}')

        # по ид получаем объекты из БД
        sender = Sender.objects.get(id=sender_id)
        message = Message.objects.get(id=message_id)
        recipients = Recipient.objects.filter(id__in=recipient_ids)

        # создаем объект рассылки
        mailing = Mailing.objects.create(sender=sender, message=message)
        mailing.recipients.add(*recipients)

        try:
            recipients_list = [recipient.email for recipient in recipients]
            # отправка сообщения
            send_mail(
                message.topic,
                message.body,
                sender.email,
                recipient_list=recipients_list,
            )

            status = 'Успешно'
            mail_server_response = 'Сообщение успешно отправлено'
            print(f'Получатели: {recipients_list}')

        except Exception as e:
            status = 'Не успешно'
            mail_server_response = f'{e}'

        # создаем объект попытки рассылки
        AttemptMailing.objects.create(status=status, mail_server_response=mail_server_response, mailing=mailing)

        return redirect('sending_messages:home')

    # def get_context_data(self, **kwargs):
    #     """ Из модели рассылки получаем отправителя, письмо и получателей и передаем в шаблон """
    #     context = super().get_context_data(**kwargs)
    #     mailing = self.get_object()
    #     context['sender'] = mailing.sender
    #     context['message'] = mailing.message
    #     context['recipients'] = mailing.recipients.all()
    #     return context


class MailingsListView(ListView):
    """ Список всех рассылок """
    model = Mailing
    paginate_by = 10
    template_name = 'mailings_list.html'
    context_object_name = 'mailings'
