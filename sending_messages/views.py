from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView, ListView, UpdateView, DeleteView, FormView

from sending_messages.forms import SenderForm, MessageForm, RecipientForm, MailingForm, RecipientListForm
from sending_messages.models import Mailing, Sender, Message, Recipient, AttemptMailing
from sending_messages.services import send_message_yandex


class MailingTemplateView(TemplateView):
    """ Главная страница """

    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        """ Передача объекта Mailing в шаблон """

        context = super().get_context_data()
        context['mailings'] = Mailing.objects.count()
        context['mailings_active'] = Mailing.objects.filter(status='Запущена').count()
        context['recipients'] = Recipient.objects.all().count()
        return context


class SenderCreateView(CreateView):
    """ Создание рассылки - отправитель(1) """

    model = Sender
    form_class = SenderForm
    template_name = 'mailing1.html'
    success_url = reverse_lazy('sending_messages:add_message')

    # def get_context_data(self, **kwargs):
    #     """ Передача в шаблон всех отправителей """
    #     context = super().get_context_data(**kwargs)
    #     context['senders'] = Sender.objects.all()
    #     return context

    def form_valid(self, form):
        """ Сохраняет объект в БД и записывает его ид в сессии """
        # сохраняет объект в БД и возвращает http ответ
        sender = super().form_valid(form)
        # сохраняет ид созданного объекта в сессии для использования на следующем этапе
        self.request.session['sender_id'] = self.object.id
        return sender


class SenderUpdateView(UpdateView):
    """ Редактирование отправителя """

    model = Sender
    form_class = SenderForm
    template_name = 'mailing1.html'

    def get_success_url(self):
        """ Перенаправление пользователя на ту страницу, с которой он пришел """
        next_url = self.request.GET.get('next', reverse_lazy('sending_messages:add_sending'))
        return next_url


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


class MessageUpdateView(UpdateView):
    """ Редактирование письма """

    model = Message
    form_class = MessageForm
    template_name = 'mailing2.html'

    def get_success_url(self):
        """ Перенаправление пользователя на ту страницу, с которой он пришел """
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('sending_messages:add_sending')


class RecipientCreateView(CreateView):
    """ Создание рассылки - получатели(3) """

    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing3.html'
    success_url = reverse_lazy('sending_messages:add_sending')

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


class RecipientListFormView(FormView):
    """ Добавить список получателей """

    form_class = RecipientListForm
    template_name = 'create_recipient_list.html'
    success_url = reverse_lazy('sending_messages:recipient_list')

    def form_valid(self, form):
        """ Сохраняет список получателей в базу данных """

        emails = form.cleaned_data.get('emails')
        if emails:
            for email in emails:
                Recipient.objects.create(email=email)
        return super().form_valid(form)


class RecipientUpdateView(UpdateView):
    """ Редактирование получателя """

    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing3.html'
    success_url = reverse_lazy('sending_messages:add_sending')


class RecipientDeleteView(DeleteView):
    """ Удаление получателя """

    model = Recipient
    template_name = 'recipient_confirm_delete.html'
    success_url = reverse_lazy('sending_messages:recipient_list')


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
        mailing.save()

        try:
            recipients_list = [recipient.email for recipient in recipients]
            # отправка сообщения
            send_message_yandex(message.topic, message.body, sender.email, recipients_list)

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


class MailingUpdateView(UpdateView):
    """ Редактирование рассылки """

    model = Mailing
    form_class = MailingForm
    template_name = 'mailing4.html'
    success_url = reverse_lazy('sending_messages:mailings_list')


class MailingDeleteView(DeleteView):
    """ Удаление рассылки """

    model = Mailing
    template_name = 'mailing_confirm_delete.html'
    success_url = reverse_lazy('sending_messages:mailings_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipients'] = self.object.recipients.all()
        return context


class MailingsListView(ListView):
    """ Список всех рассылок """
    model = Mailing
    paginate_by = 10
    template_name = 'mailings_list.html'
    context_object_name = 'mailings'

    def get_context_data(self, **kwargs):
        """ Пагинация появится, только если активных рассылок будет больше, чем указано в paginate_by """
        context = super().get_context_data(**kwargs)
        mailings = Mailing.objects.all().count()
        if mailings > self.paginate_by:
            context['show_pagination'] = True
        return context


class MailingsActiveListView(ListView):
    """ Список активных рассылок """
    model = Mailing
    paginate_by = 10
    template_name = 'mailings_active_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        """ Только активные рассылки """

        return Mailing.objects.filter(status='Запущена')

    def get_context_data(self, **kwargs):
        """ Пагинация появится, только если активных рассылок будет больше, чем указано в paginate_by """
        context = super().get_context_data(**kwargs)
        if self.get_queryset().count() > self.paginate_by:
            context['show_pagination'] = True
        return context


class MailingDetailView(DetailView):
    """ Информация о рассылке """
    model = Mailing
    template_name = 'mailing_detail.html'
    context_object_name = 'mailing'


class RecipientListView(ListView):
    """ Список получателей """
    model = Recipient
    template_name = 'recipient_list1.html'
    context_object_name = 'recipients'


class RecipientDetailView(DetailView):
    """ Информация о получателе """
    model = Recipient
    template_name = 'recipient_detail.html'
    context_object_name = 'recipient'


class SendMailingView(View):
    """ Отправка уже существующей рассылки """

    def get(self, request, *args, **kwargs):
        # получаем ид рассылки, а по ид получаем саму рассылку
        mailing_id = self.kwargs.get('pk')
        mailing = get_object_or_404(Mailing, pk=mailing_id)

        # отправка сообщения
        send_message_yandex(mailing.message.topic, mailing.message.body, mailing.sender, mailing.recipients.all())

        return redirect('sending_messages:mailing_ok')


class MailingOkTemplateView(TemplateView):
    """ Рассылка успешно отправлена """

    template_name = 'mailing_ok.html'
