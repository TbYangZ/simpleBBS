# Generated by Django 5.1.2 on 2024-11-05 05:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_user_is_authenticated'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_authenticated',
        ),
    ]
