from django.urls import path
from sending_messages.apps import SendingMessagesConfig
from sending_messages.views import MailingTemplateView, SenderCreateView, MessageCreateView, RecipientCreateView, \
    SendingDetailView

app_name = SendingMessagesConfig.name

urlpatterns = [
    path('home/', MailingTemplateView.as_view(), name='home'),
    path('mailing/add_sender/', SenderCreateView.as_view(), name='add_sender'),
    path('mailing/add_message/', MessageCreateView.as_view(), name='add_message'),
    path('mailing/add_recipient/', RecipientCreateView.as_view(), name='add_recipient'),
    path('mailing/<int:pk>/sending/', SendingDetailView.as_view(), name='sending'),
]
