# Generated by Django 5.1 on 2024-08-27 10:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0005_order_stream_order_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stream',
            old_name='owner',
            new_name='user',
        ),
    ]