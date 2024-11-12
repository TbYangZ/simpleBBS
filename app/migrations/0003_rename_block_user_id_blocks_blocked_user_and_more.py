# Generated by Django 5.1.2 on 2024-11-11 09:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_rename_auther_id_post_author'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blocks',
            old_name='block_user_id',
            new_name='blocked_user',
        ),
        migrations.RenameField(
            model_name='blocks',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='follow',
            old_name='followee_id',
            new_name='followee',
        ),
        migrations.RenameField(
            model_name='follow',
            old_name='follower_id',
            new_name='follower',
        ),
        migrations.RenameField(
            model_name='like',
            old_name='post_id',
            new_name='post',
        ),
        migrations.RenameField(
            model_name='like',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='review',
            old_name='post_id',
            new_name='post',
        ),
        migrations.RenameField(
            model_name='review',
            old_name='reply_id',
            new_name='reply',
        ),
        migrations.RenameField(
            model_name='review',
            old_name='user_id',
            new_name='user',
        ),
    ]