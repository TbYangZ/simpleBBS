from django.http import HttpResponse
from django.shortcuts import render, redirect

from app.models import Post


# Create your views here.

def index(request):
    return HttpResponse('Hello, Django!')


def post_list(request):
    if request.method == 'POST':
        content = request.POST['content']
        Post.objects.create(author='Name', content=content)
        return redirect('post_list')
    posts = Post.objects.all()
    return render(request, 'post_list.html', {'posts': posts})
