# Generated by Django 5.1.3 on 2024-12-18 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sending_messages", "0002_alter_sender_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="body",
            field=models.TextField(help_text="Введите текст письма", verbose_name="Текст письма"),
        ),
    ]
