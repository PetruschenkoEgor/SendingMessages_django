from django.contrib import admin

from sending_messages.models import Recipient, Message, Sender, Mailing, AttemptMailing


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'fio')
    ordering = ('fio',)
    search_fields = ('email', 'fio')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic')


@admin.register(Sender)
class SenderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email')
    ordering = ('name',)
    search_fields = ('name', 'email')


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'status')
    list_filter = ('status',)


@admin.register(AttemptMailing)
class AttemptMailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_time_attempt', 'status', 'mailing')
    list_filter = ('status',)
