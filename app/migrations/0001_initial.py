# Generated by Django 5.1.2 on 2024-11-11 08:57

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('max_floor', models.IntegerField(default=1)),
                ('likes', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=150, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_authenticated', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('likes', models.IntegerField(default=0)),
                ('floors', models.IntegerField(default=0)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.post')),
                ('reply_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.review')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.user')),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='auther_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_auther', to='app.user'),
        ),
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('receiver_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='app.user')),
                ('sender_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='app.user')),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('like_time', models.DateTimeField(auto_now_add=True)),
                ('post_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='liked_post', to='app.post')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='like_user', to='app.user')),
            ],
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('follow_time', models.DateTimeField(auto_now_add=True)),
                ('followee_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followee', to='app.user')),
                ('follower_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower', to='app.user')),
            ],
        ),
        migrations.CreateModel(
            name='Blocks',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('block_time', models.DateTimeField(auto_now_add=True)),
                ('block_user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocked_user', to='app.user')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='block_user', to='app.user')),
            ],
        ),
    ]