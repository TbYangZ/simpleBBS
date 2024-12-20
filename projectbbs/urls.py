"""
URL configuration for projectbbs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from app import views, consumers

urlpatterns = [
    path('', views.post_list, name='main_page'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('post_detail/<int:post_id>/', views.post_detail, name='post_detail'),
    path('user/<int:user_id>/', views.user_main_page, name='user_main_page'),
    path('user/<int:user_id>/follow/', views.follow_user, name='follow_user'),
    path('user/<int:user_id>/unfollow/', views.unfollow_user, name='unfollow_user'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('chat_room/', views.public_chat_room, name='public_chat_room'),
    path('chat_room/<int:server_id>/', views.public_chat_room_in_server, name='public_chat_room_in_server'),
    path('chat_room/<int:server_id>/<int:channel_id>/', views.channel, name='channel'),
    path('send_message/', views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('message/<int:message_id>/', views.message_detail, name='message_detail'),
    path('chat_room/', views.public_chat_room, name='public_chat_room'),
    path('chat_room/<int:server_id>/', views.public_chat_room_in_server, name='public_chat_room_in_server'),
    path('chat_room/<int:server_id>/<int:channel_id>/', views.channel, name='channel'),
    path('chat/', views.chat_list, name='chat_list'),
    path('chat/<int:user_id>/', views.chat_detail, name='chat_detail'),
    path('admin/', views.admin_dashboard, name='admin'),
    path('admin/dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('admin/user', views.admin_user, name='admin_user'),
    path('admin/edit_user/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),
    path('admin/delete_user/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin/post', views.admin_post, name='admin_post'),
    path('admin/delete_post/<int:post_id>/', views.admin_delete_post, name='admin_delete_post'),
    path('admin/review/', views.admin_review, name='admin_review'),
]