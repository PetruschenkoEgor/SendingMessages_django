from django.urls import path
from sending_messages.apps import SendingMessagesConfig
from sending_messages.views import MailingTemplateView, MessageCreateView, \
    SendingCreateView, MailingsListView, MailingsActiveListView, RecipientListView, MailingDetailView, \
    RecipientDetailView, MessageUpdateView, RecipientUpdateView, MailingOkTemplateView, \
    SendMailingView, MailingUpdateView, MailingDeleteView, RecipientDeleteView, RecipientListFormView, \
    RecipientCreateView, MessageListView, MessageDeleteView, MessageDetailView

app_name = SendingMessagesConfig.name

urlpatterns = [
    path('home/', MailingTemplateView.as_view(), name='home'),
    path('mailing/add_message/', MessageCreateView.as_view(), name='add_message'),
    path('mailing/add_recipient/', RecipientCreateView.as_view(), name='add_recipient'),
    # path('mailing/add_recipients/', RecipientListMailingFormView.as_view(), name='add_recipients'),
    path('mailing/add_recipient_list/', RecipientListFormView.as_view(), name='add_recipient_list'),
    path('mailing/add_sending/', SendingCreateView.as_view(), name='add_sending'),
    path('mailings/', MailingsListView.as_view(), name='mailings_list'),
    path('mailings_active/', MailingsActiveListView.as_view(), name='mailings_active_list'),
    path('recipients/', RecipientListView.as_view(), name='recipient_list'),
    path('mailing/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('recipient/<int:pk>/', RecipientDetailView.as_view(), name='recipient_detail'),
    path('message/<int:pk>/edit/', MessageUpdateView.as_view(), name='edit_message'),
    path('recipient/<int:pk>/edit/', RecipientUpdateView.as_view(), name='edit_recipient'),
    path('mailing/<int:pk>/edit/', MailingUpdateView.as_view(), name='edit_mailing'),
    path('mailings/<int:pk>/send/', SendMailingView.as_view(), name='send'),
    path('mailing_ok/', MailingOkTemplateView.as_view(), name='mailing_ok'),
    path('mailing/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),
    path('recipient/<int:pk>/delete/', RecipientDeleteView.as_view(), name='recipient_delete'),
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('message/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),
    path('message/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
]
