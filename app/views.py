from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from app.models import Post, UserBackend
from app.models import User


# Create your views here.

def index(request):
    return HttpResponse('Hello, Django!')


def post_list(request):
    if request.method == 'POST':
        content = request.POST['content']
        Post.objects.create(author=request.user.username, content=content)
        return redirect('post_list')
    posts = Post.objects.all()
    return render(request, 'post_list.html', {'posts': posts})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request=request, username=username, password=password)
        if user is not None:
            login(request, user)
            print(user.is_authenticated)
            return redirect('post_list')
        else:
            messages.error(request, '用户名或密码错误')
            return redirect('login')
    return render(request, 'login_page.html')


def logout_view(request):
    logout(request)
    return redirect('post_list')


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
            return redirect('post_list')
    return render(request, 'register_page.html')