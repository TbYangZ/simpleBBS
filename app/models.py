from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


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
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender_id}: {self.content}"


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