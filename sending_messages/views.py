from django.core.mail import send_mail
from django.forms import forms
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView, ListView, UpdateView, DeleteView, FormView

from config.settings import EMAIL_HOST_USER
from sending_messages.forms import MessageForm, RecipientForm, MailingForm, RecipientListForm
from sending_messages.models import Mailing, Message, Recipient, AttemptMailing
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
        context['messages'] = Message.objects.all().count()
        attempts = AttemptMailing.objects.all()
        context['attempt_ok'] = sum([attempt.sending_count_ok for attempt in attempts])
        context['attempt_error'] = sum([attempt.sending_count_error for attempt in attempts])
        context['messages_count'] = sum([attempt.count_messages for attempt in attempts])
        return context


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


class RecipientCreateView(CreateView):
    """ Создание получателя """

    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing3.html'
    success_url = reverse_lazy('sending_messages:recipient_list')

    def form_valid(self, form):
        """ Сохраняет объект в БД """
        recipient = super().form_valid(form)

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
                if not Recipient.objects.filter(email=email).exists():
                    Recipient.objects.create(email=email)
        return super().form_valid(form)


class RecipientUpdateView(UpdateView):
    """ Редактирование получателя """

    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing3.html'
    success_url = reverse_lazy('sending_messages:recipient_list')


class RecipientDeleteView(DeleteView):
    """ Удаление получателя """

    model = Recipient
    template_name = 'recipient_confirm_delete.html'
    success_url = reverse_lazy('sending_messages:recipient_list')


class MessageListView(ListView):
    """ Список шаблонов писем """

    model = Message
    template_name = 'message_list.html'
    context_object_name = 'messages'


class MessageDetailView(DetailView):
    """ Информация о письме """

    model = Message
    template_name = 'message_detail.html'
    context_object_name = 'message'


class MessageCreateView(CreateView):
    """ Создание сообщения """

    model = Message
    form_class = MessageForm
    template_name = 'mailing2.html'
    success_url = reverse_lazy('sending_messages:message_list')

    def form_valid(self, form):
        """ Сохраняет объект в БД """
        # сохраняет объект в БД и возвращает http ответ
        message = super().form_valid(form)
        return message


class MessageUpdateView(UpdateView):
    """ Редактирование письма """

    model = Message
    form_class = MessageForm
    template_name = 'mailing2.html'
    success_url = reverse_lazy('sending_messages:message_list')


class MessageDeleteView(DeleteView):
    """ Удаление письма """

    model = Message
    template_name = 'message_confirm_delete.html'
    success_url = reverse_lazy('sending_messages:message_list')


class MailingsListView(ListView):
    """ Список всех рассылок """
    model = Mailing
    paginate_by = 10
    template_name = 'mailings_list.html'
    context_object_name = 'mailings'

    def get_context_data(self, **kwargs):
        """ Пагинация появится, только если рассылок будет больше, чем указано в paginate_by """
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

    def get_context_data(self, **kwargs):
        """ Все получатели """

        context = super().get_context_data(**kwargs)
        context['recipients'] = self.object.recipients.all()
        return context


class SendingCreateView(CreateView):
    """ Создание рассылки """

    model = Mailing
    form_class = MailingForm
    template_name = 'mailing4.html'
    success_url = reverse_lazy('sending_messages:mailings_list')

    def get_initial(self):
        """ Автоматическое заполнение формы всеми активными получателями """
        initial = super().get_initial()

        initial['recipients'] = Recipient.objects.filter(active=True)
        return initial

    def form_valid(self, form):
        """ Сохранение рассылки и ее попытки, отправка сообщения """

        response = super().form_valid(form)
        mailing = self.object

        # все активные получатели
        recipients_existing = Recipient.objects.filter(active=True)
        print(f'Количество получателей: {recipients_existing.count()}')

        # добавляем получателей
        mailing.recipients.add(*recipients_existing)
        mailing.save()

        try:
            recipients_list = [recipient.email for recipient in recipients_existing]
            # отправка сообщения
            send_message_yandex(mailing.message.topic, mailing.message.body, EMAIL_HOST_USER, recipients_list)

            status = 'Успешно'
            mail_server_response = 'Сообщение успешно отправлено'
            # создаем объект попытки рассылки
            AttemptMailing.objects.create(status=status, mail_server_response=mail_server_response, mailing=mailing)
            attempt = AttemptMailing.objects.get(mailing=mailing)
            attempt.sending_count_ok += 1
            attempt.count_messages += len(recipients_list)
            attempt.save()

        except Exception as e:
            status = 'Не успешно'
            mail_server_response = f'{e}'
            # создаем объект попытки рассылки
            AttemptMailing.objects.create(status=status, mail_server_response=mail_server_response, mailing=mailing)
            attempt = AttemptMailing.objects.get(mailing=mailing)
            attempt.sending_count_error += 1
            attempt.save()

        return response


class SendMailingView(View):
    """ Отправка уже существующей рассылки """

    def get(self, request, *args, **kwargs):
        """ Отправка сообщения и увеличение количества раз отправления данной рассылки """
        # получаем ид рассылки, а по ид получаем саму рассылку
        mailing_id = self.kwargs.get('pk')
        mailing = get_object_or_404(Mailing, pk=mailing_id)

        try:
            # отправка сообщения
            recipients = mailing.recipients.all()
            send_message_yandex(mailing.message.topic, mailing.message.body, EMAIL_HOST_USER, recipients)
            # увеличение количества раз отправления данной рассылки
            attempt = AttemptMailing.objects.get(mailing=mailing)
            attempt.sending_count_ok += 1
            attempt.count_messages += recipients.count()
            attempt.save()

        except Exception as e:
            status = 'Не успешно'
            mail_server_response = f'{e}'
            attempt = AttemptMailing.objects.get(mailing=mailing)
            attempt.status = status
            attempt.mail_server_response = mail_server_response
            attempt.sending_count_error += 1
            attempt.save()

        return redirect('sending_messages:mailings_list')


# class MailingOkTemplateView(TemplateView):
#     """ Рассылка успешно отправлена """
#
#     template_name = 'mailing_ok.html'
#
#     def get_context_data(self, **kwargs):
#         """ Передача в шаблон успешная или неуспешная отправка """
#
#         context = super().get_context_data()
#         context


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












# class SenderCreateView(CreateView):
#     """ Создание рассылки - отправитель(1) """
#
#     model = Sender
#     form_class = SenderForm
#     template_name = 'mailing1.html'
#     success_url = reverse_lazy('sending_messages:add_message')
#
#     def form_valid(self, form):
#         """ Сохраняет объект в БД и записывает его ид в сессии """
#         # # сохраняет объект в БД и возвращает http ответ
#         # sender = super().form_valid(form)
#         # # сохраняет ид созданного объекта в сессии для использования на следующем этапе
#         # self.request.session['sender_id'] = self.object.id
#         # return sender
#
#         email = form.cleaned_data.get('email')
#         sender = Sender.objects.filter(email=email).first()
#         if sender:
#             self.request.session['sender_id'] = sender.id
#         else:
#             sender = form.save()
#             self.request.session['sender_id'] = sender.id
#         return redirect(self.success_url)
#
#     def form_invalid(self, form):
#         """ Если email уже существует в БД, то используем его же, без сохранения в БД """
#         # если форма не валидирована, записывает ид отправителя в сессию
#         email = form.cleaned_data.get('email')
#         sender = Sender.objects.filter(email=email).first()
#         if sender:
#             self.request.session['sender_id'] = sender.id
#         return redirect(self.success_url)


# class SenderUpdateView(UpdateView):
#     """ Редактирование отправителя """
#
#     model = Sender
#     form_class = SenderForm
#     template_name = 'mailing1.html'
#
#     def get_success_url(self):
#         """ Перенаправление пользователя на ту страницу, с которой он пришел """
#         next_url = self.request.GET.get('next', reverse_lazy('sending_messages:add_sending'))
#         return next_url


# class RecipientCreateView(CreateView):
#     """ Создание рассылки - получатели(3) """
#
#     model = Recipient
#     form_class = RecipientForm
#     template_name = 'mailing3.html'
#     success_url = reverse_lazy('sending_messages:add_sending')
#
#     def form_valid(self, form):
#         """ Сохраняет объект в БД и записывает его ид в сессии """
#         # сохраняет объект в БД и возвращает http ответ
#         recipient = super().form_valid(form)
#         # создаем список с идентификаторами получателей и добавляем в него иды
#         recipient_ids = self.request.session.get('recipient_ids', [])
#         recipient_ids.append(self.object.id)
#         # сохраняет ид созданного объекта в сессии для использования на следующем этапе
#         self.request.session['recipient_ids'] = recipient_ids
#         return recipient








# class RecipientListMailingFormView(FormView):
#     """ Создание рассылки - получатели(3) """
#
#     form_class = RecipientListForm
#     template_name = 'mailing3_create_recipient_list.html'
#     success_url = reverse_lazy('sending_messages:add_sending')
#
#     def form_valid(self, form):
#         """ Сохраняет список получателей в базу данных """
#
#         emails = form.cleaned_data.get('emails')
#         if emails:
#             # создаем список с идентификаторами получателей и добавляем в него иды
#             # recipient_ids = self.request.session.get('recipient_ids', [])
#             for email in emails:
#                 Recipient.objects.create(email=email)
#
#                 # recipient_ids.append(self.object.id)
#             # сохраняет ид созданного объекта в сессии для использования на следующем этапе
#             # self.request.session['recipient_ids'] = recipient_ids
#         return super().form_valid(form)
