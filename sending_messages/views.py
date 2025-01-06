from django.contrib.auth.mixins import LoginRequiredMixin
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


class InfoTemplateView(TemplateView):
    """ Информация о сайте """

    template_name = 'info.html'


class MailingTemplateView(LoginRequiredMixin, TemplateView):
    """ Главная страница """

    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        """ Передача объекта Mailing в шаблон """

        context = super().get_context_data()
        context['mailings'] = Mailing.objects.filter(owner=self.request.user).count()
        context['mailings_active'] = Mailing.objects.filter(status='Запущена', owner=self.request.user).count()
        context['recipients'] = Recipient.objects.filter(owner=self.request.user).count()
        context['messages'] = Message.objects.filter(owner=self.request.user).count()
        attempts = AttemptMailing.objects.filter(owner=self.request.user)
        context['attempt_ok'] = sum([attempt.sending_count_ok for attempt in attempts])
        context['attempt_error'] = sum([attempt.sending_count_error for attempt in attempts])
        context['messages_count'] = sum([attempt.count_messages for attempt in attempts])
        return context


class RecipientListView(LoginRequiredMixin, ListView):
    """ Список получателей """

    model = Recipient
    template_name = 'recipient_list1.html'
    context_object_name = 'recipients'

    def get_queryset(self):
        """ Получатели рассылки только текущего пользователя """

        return Recipient.objects.filter(owner=self.request.user)


class RecipientDetailView(LoginRequiredMixin, DetailView):
    """ Информация о получателе """
    model = Recipient
    template_name = 'recipient_detail.html'
    context_object_name = 'recipient'


class RecipientCreateView(LoginRequiredMixin, CreateView):
    """ Создание получателя, устанавливаем владельца получателя """

    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing3.html'
    success_url = reverse_lazy('sending_messages:recipient_list')

    def form_valid(self, form):
        """ Сохраняет объект в БД """

        email = form.cleaned_data['email']
        recipient, created = Recipient.objects.get_or_create(email=email, owner=self.request.user)
        if created:
            recipient.fio = form.cleaned_data.get('fio', recipient.fio)
            recipient.comment = form.cleaned_data.get('comment', recipient.comment)
            recipient.active = form.cleaned_data.get('active', recipient.active)
            recipient.save()
        else:
            # Если получатель уже существует, добавляем сообщение об ошибке
            form.add_error('email', 'Получатель с таким email уже существует.')
            return self.form_invalid(form)

        return super().form_valid(form)


class RecipientListFormView(LoginRequiredMixin, FormView):
    """ Добавить список получателей, установка владельца получателей """

    form_class = RecipientListForm
    template_name = 'create_recipient_list.html'
    success_url = reverse_lazy('sending_messages:recipient_list')

    def form_valid(self, form):
        """ Сохраняет список получателей в базу данных """

        emails = form.cleaned_data.get('emails')
        if emails:
            for email in emails:
                if not Recipient.objects.filter(email=email, owner=self.request.user).exists():
                    Recipient.objects.create(email=email, owner=self.request.user)
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    """ Редактирование получателя """

    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing3.html'
    success_url = reverse_lazy('sending_messages:recipient_list')


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    """ Удаление получателя """

    model = Recipient
    template_name = 'recipient_confirm_delete.html'
    success_url = reverse_lazy('sending_messages:recipient_list')


class MessageListView(LoginRequiredMixin, ListView):
    """ Список шаблонов писем """

    model = Message
    template_name = 'message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        """ Сообщения текущего пользователя """

        return Message.objects.filter(owner=self.request.user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    """ Информация о письме """

    model = Message
    template_name = 'message_detail.html'
    context_object_name = 'message'


class MessageCreateView(LoginRequiredMixin, CreateView):
    """ Создание сообщения """

    model = Message
    form_class = MessageForm
    template_name = 'mailing2.html'
    success_url = reverse_lazy('sending_messages:message_list')

    def form_valid(self, form):
        """ Сохраняет объект в БД """

        form.instance.owner = self.request.user

        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    """ Редактирование письма """

    model = Message
    form_class = MessageForm
    template_name = 'mailing2.html'
    success_url = reverse_lazy('sending_messages:message_list')


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    """ Удаление письма """

    model = Message
    template_name = 'message_confirm_delete.html'
    success_url = reverse_lazy('sending_messages:message_list')


class MailingsListView(LoginRequiredMixin, ListView):
    """ Список всех рассылок """
    model = Mailing
    paginate_by = 10
    template_name = 'mailings_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        """ Рассылки только текущего пользователя """

        return Mailing.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        """ Пагинация появится, только если рассылок будет больше, чем указано в paginate_by """
        context = super().get_context_data(**kwargs)
        mailings = Mailing.objects.filter(owner=self.request.user).count()
        if mailings > self.paginate_by:
            context['show_pagination'] = True
        return context


class MailingsActiveListView(LoginRequiredMixin, ListView):
    """ Список активных рассылок """
    model = Mailing
    paginate_by = 10
    template_name = 'mailings_active_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        """ Только активные рассылки и текущего пользователя """

        return Mailing.objects.filter(status='Запущена', owner=self.request.user)

    def get_context_data(self, **kwargs):
        """ Пагинация появится, только если активных рассылок будет больше, чем указано в paginate_by """
        context = super().get_context_data(**kwargs)
        if self.get_queryset().count() > self.paginate_by:
            context['show_pagination'] = True

        return context


class MailingDetailView(LoginRequiredMixin, DetailView):
    """ Информация о рассылке """
    model = Mailing
    template_name = 'mailing_detail.html'
    context_object_name = 'mailing'

    def get_context_data(self, **kwargs):
        """ Все получатели """

        context = super().get_context_data(**kwargs)
        context['recipients'] = self.object.recipients.all()
        return context


class SendingCreateView(LoginRequiredMixin, CreateView):
    """ Создание рассылки """

    model = Mailing
    form_class = MailingForm
    template_name = 'mailing4.html'
    success_url = reverse_lazy('sending_messages:mailings_list')

    def get_form_kwargs(self):
        """ При создании рассылки, пользователь может выбрать только свои сообщения и получателей """

        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        """ Автоматическое заполнение формы всеми активными получателями """

        initial = super().get_initial()

        initial['recipients'] = Recipient.objects.filter(active=True, owner=self.request.user)
        return initial

    def form_valid(self, form):
        """ Сохранение рассылки и ее попытки, отправка сообщения, устанавливаем владельца рассылки """

        form.instance.owner = self.request.user
        response = super().form_valid(form)
        mailing = self.object

        # все активные получатели
        recipients_existing = Recipient.objects.filter(active=True, owner=self.request.user)
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
            attempt, created = AttemptMailing.objects.get_or_create(mailing=mailing)
            attempt.status = status
            attempt.mail_server_response = mail_server_response
            attempt.sending_count_ok += 1
            attempt.count_messages += len(recipients_list)

        except Exception as e:
            status = 'Не успешно'
            mail_server_response = f'{e}'
            # создаем объект попытки рассылки
            attempt, created = AttemptMailing.objects.get_or_create(mailing=mailing)
            attempt.status = status
            attempt.mail_server_response = mail_server_response
            attempt.sending_count_error += 1

        finally:
            attempt.owner = self.request.user
            attempt.save()

        return response


class SendMailingView(LoginRequiredMixin, View):
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

        except Exception as e:
            status = 'Не успешно'
            mail_server_response = f'{e}'
            attempt = AttemptMailing.objects.get(mailing=mailing)
            attempt.status = status
            attempt.mail_server_response = mail_server_response
            attempt.sending_count_error += 1

        finally:
            attempt.owner = self.request.user
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


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    """ Редактирование рассылки """

    model = Mailing
    form_class = MailingForm
    template_name = 'mailing4.html'
    success_url = reverse_lazy('sending_messages:mailings_list')


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    """ Удаление рассылки """

    model = Mailing
    template_name = 'mailing_confirm_delete.html'
    success_url = reverse_lazy('sending_messages:mailings_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipients'] = self.object.recipients.all()
        return context


class AttemptMailingListView(LoginRequiredMixin, ListView):
    """ Список попыток рассылки """

    model = AttemptMailing
    template_name = 'statistic.html'
    context_object_name = 'attempts'






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
