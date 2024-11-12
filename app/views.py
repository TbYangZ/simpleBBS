from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from app.models import Post, UserBackend, Review, Follow, Messages, Blocks
from app.models import User


# Create your views here.

def index(request):
    return HttpResponse('Hello, Django!')


def post_list(request):
    if request.method == 'POST':
        content = request.POST['content']
        Post.objects.create(author=request.user, content=content)
        return redirect('main_page')
    posts = Post.objects.all()
    simplified_posts = []
    for post in posts:
        post.content = post.content[:20]
        username = post.author.username
        simplified_posts.append([post, username])
    simplified_posts = sorted(simplified_posts, key=lambda x: x[0].created_at, reverse=True)
    return render(request, 'main_page.html', {'posts': simplified_posts})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request=request, username=username, password=password)
        if user is not None:
            login(request, user)
            print(user.is_authenticated)
            return redirect('main_page')
        else:
            messages.error(request, '用户名或密码错误')
            return redirect('login')
    return render(request, 'login_page.html')


def logout_view(request):
    logout(request)
    return redirect('main_page')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
        elif password != password_confirm:
            messages.error(request, '两次密码不一致')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('main_page')
    return render(request, 'register_page.html')


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.method == 'POST':
        content = request.POST['content']
        Review.objects.create(post=post, user=request.user, content=content)
        return redirect(reverse('post_detail', args=[post_id]))
    author_name = post.get_author_name()
    reviews = []
    for review in Review.objects.filter(post=post):
        reviews.append([review, review.get_user_name()])
    return render(request, 'post_detail.html', {'post': post, "author_name": author_name, 'reviews': reviews})


def user_main_page(request, user_id):
    user = User.objects.get(id=user_id)
    current_user = request.user

    if user is None or user.is_active is False:
        return render(request, 'no_such_user.html')

    is_blocked = Blocks.objects.filter(user=user, blocked_user=current_user)
    if is_blocked:
        return render(request, 'blocked.html', {'user': user, 'current_user': current_user})

    posts = Post.objects.filter(author=user)

    return render(request, 'user_main_page.html', {'user': user, 'posts': posts})


def follower_page(request, user_id):
    user = User.objects.get(id=user_id)
    followers = Follow.objects.filter(following=user)
    return render(request, 'follower_page.html', {'user': user, 'followers': followers})


def message_page(request):
    user = request.user
    private_messages = Messages.objects.filter(receiver_id=user.id)
    return render(request, 'message_page.html', {'user': user, 'messages': private_messages})
