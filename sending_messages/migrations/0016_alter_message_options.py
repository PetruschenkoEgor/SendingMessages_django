# Generated by Django 5.1.3 on 2025-01-07 09:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sending_messages', '0015_alter_mailing_options_alter_recipient_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'permissions': [('can_view_all_messages', 'Can view all messages')], 'verbose_name': 'Сообщение', 'verbose_name_plural': 'Сообщения'},
        ),
    ]
