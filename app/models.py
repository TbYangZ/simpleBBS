from zoneinfo import ZoneInfo

import markdown
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.utils.timezone import localtime
from django.views.decorators.csrf import csrf_exempt
import json
# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)


class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_authenticated = models.BooleanField(default=True)

    objects = UserManager()

    def __str__(self):
        return f"{self.id}: {self.username}"

    # 设置密码时，使用哈希加密存储密码
    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    # 检查密码
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def is_in_server(self, server):
        return ServerUser.objects.filter(server_id=server.id, user_id=self.id).exists()


class UserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_author')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    max_floor = models.IntegerField(default=1)
    likes = models.IntegerField(default=0)

    def get_author_name(self):
        return User.objects.get(id=self.author_id).username

    def __str__(self):
        return f"{self.author_id}: {self.content}"


class Review(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    likes = models.IntegerField(default=0)
    floors = models.IntegerField(default=0)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id}: {self.content}"

    def get_user_name(self):
        return User.objects.get(id=self.user_id).username

    def get_reply_id(self):
        return Review.objects.filter(reply_id=self.id)

    def get_likes(self):
        return Review.objects.filter(likes=self.likes)


class Messages(models.Model):
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', default=None)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', default=None)
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender} to {self.receiver}: {self.content[:30]}"


class Follow(models.Model):
    id = models.AutoField(primary_key=True)
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    followee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followee')
    follow_time = models.DateTimeField(auto_now_add=True)

    def get_follower_name(self):
        return User.objects.get(id=self.follower_id).username

    def get_followee_name(self):
        return User.objects.get(id=self.followee_id).username

    def __str__(self):
        return f"{self.follower_id}: {self.followee_id}"


class Like(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='like_user')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='liked_post')
    like_time = models.DateTimeField(auto_now_add=True)

    def get_user_name(self):
        return User.objects.get(id=self.user_id).username

    def __str__(self):
        return f"{self.get_user_name()}: {self.post_id}"


class Blocks(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='block_user')
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_user')
    block_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id}: {self.blocked_user}"


class Server(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='server_owner')
    status = models.BooleanField(default=True)
    secret = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_owner_name(self):
        return User.objects.get(id=self.owner_id).username

    def __str__(self):
        return self.name


class Channel(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='channel_server')
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_server_name(self):
        return Server.objects.get(id=self.server_id).name

    def __str__(self):
        return f'{self.name}'


class ServerChannel(models.Model):
    id = models.AutoField(primary_key=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='server')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='server_channel')
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.server.name}: {self.name}"


class ServerUser(models.Model):
    id = models.AutoField(primary_key=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='user_server')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='server_user')
    join_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.server.name}: {self.user}"


class ServerBlock(models.Model):
    id = models.AutoField(primary_key=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='block_server')
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='server_blocked_user')
    block_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.server.name}: {self.blocked_user}"


class ChannelMessage(models.Model):
    id = models.AutoField(primary_key=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='channel_message')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='channel_message_user')
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.channel.name}: {self.user.username}"


class SystemMessage(models.Model):
    TEXT = 'text'
    CHOICE = 'choice'
    MESSAGE_TYPE_CHOICE = [
        (TEXT, 'text'),
        (CHOICE, 'choice'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='system_message_user')
    content = models.TextField()
    message_type = models.CharField(max_length=50, choices=MESSAGE_TYPE_CHOICE, default=TEXT)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content}"


def create_server(server_name, owner, is_secret=False):
    server = Server.objects.create(name=server_name, owner=owner, secret=is_secret)
    ServerUser.objects.create(server=server, user=owner)
    default_channel = Channel.objects.create(name='general', server=server)
    ServerChannel.objects.create(server=server, channel=default_channel)
    return server


def create_channel(channel_name, server, current_user):
    if not server.owner_id == current_user.id:
        raise ValueError("You are not the owner of this server.")
    channel = Channel.objects.create(name=channel_name, server=server)
    ServerChannel.objects.create(server=server, channel=channel)
    return channel


SUCCESS = 0
ERROR_ALREADY_IN_SERVER = -1
ERROR_BLOCKED_BY_SERVER_OWNER = -2
ERROR_SECRET_SERVER = -3


def join_server(server_id, user):
    server = Server.objects.get(id=server_id)
    if ServerUser.objects.filter(server_id=server.id, user_id=user.id).exists():
        return ERROR_ALREADY_IN_SERVER, "You have already joined this server."
    if ServerBlock.objects.filter(server_id=server.id, blocked_user_id=user.id).exists():
        return ERROR_BLOCKED_BY_SERVER_OWNER, "You are blocked from this server."
    if server.secret:
        return ERROR_SECRET_SERVER, "This server is secret."
    ServerUser.objects.create(server=server, user=user)
    return SUCCESS, "Join server successfully."


def get_message_from_channel(channel):
    return ChannelMessage.objects.filter(channel_id=channel.id)


def get_channels_from_server(server):
    query_set = ServerChannel.objects.filter(server_id=server.id)
    channel_list = []
    for server_channel in query_set:
        channel_list.append(Channel.objects.get(id=server_channel.channel_id))
    return channel_list


def send_system_message(user, content):
    SystemMessage.objects.create(user=user, content=content)


def get_server_list(user):
    query_set = ServerUser.objects.filter(user_id=user.id)
    server_list = []
    for server_user in query_set:
        server_list.append(Server.objects.get(id=server_user.server_id))
    return server_list


def get_channel_history(channel):
    query_set = ChannelMessage.objects.filter(channel_id=channel.id)
    history = []
    for message in query_set:
        history.append({
            'user_name': User.objects.get(id=message.user_id).username,
            'content': message.content,
            'time': localtime(message.time, ZoneInfo("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M:%S'),
        })
    return history


class PrivateMessage(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='private_messages_sent'
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='private_messages_received'
    )

    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']