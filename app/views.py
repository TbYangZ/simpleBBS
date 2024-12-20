from datetime import datetime
from zoneinfo import ZoneInfo

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Max
from django.utils.timezone import localtime

from app.models import *
from app.models import User
import markdown
from app.forms import PostForm, MessageForm

# Create your views here.


def index(request):
    return HttpResponse('Hello, Django!')


def post_list(request):
    if request.method == 'POST':
        content = request.POST['content']
        Post.objects.create(author=request.user, content=content)
        return redirect('main_page')
    search_content = request.GET.get('search_content', '')
    posts = Post.objects.all()
    if search_content:
        posts = posts.filter(Q(content__icontains=search_content) | Q(author__username__icontains=search_content))

    start_time = request.GET.get('start_time', '')
    if start_time:
        posts = posts.filter(created_at__gte=start_time)

    end_time = request.GET.get('end_time', '')
    if end_time:
        posts = posts.filter(created_at__lte=end_time)

    simplified_posts = []
    for post in posts:
        post.content = post.content[:20]
        post.created_at = localtime(post.created_at, ZoneInfo("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M')
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
            print(user.is_superuser)
            return redirect('main_page')
        else:
            messages.error(request, '用户名或密码错误')
            return redirect('login')
    return render(request, 'login_page.html')


@login_required
def admin_view(request):
    user = request.user
    if not user.is_superuser:
        return HttpResponseForbidden()
    if request.method == 'POST':
        username = request.POST['username']
        user = User.objects.get(username=username)
        user.is_active = False
        user.save()
        return redirect('admin_page')
    users = User.objects.all()
    posts = Post.objects.all()
    servers = Server.objects.all()
    channels = {
        server: get_channels_from_server(server)
        for server in servers
    }
    context = {
        'users': users,
        'posts': posts,
    }
    return render(request, 'admin_page.html')


@login_required
def admin_dashboard(request):
    context = {
        'user_count': User.objects.count(),
        'post_count': Post.objects.count(),
        'comment_count': Review.objects.count(),
        'server_count': Server.objects.count(),
    }
    return render(request, 'admin_dashboard.html', context)


@login_required
def admin_user(request):
    query = request.GET.get('query_user_name', '')
    users = User.objects.filter(username__icontains=query, is_superuser=False)

    date_start = request.GET.get('start_time', '')
    if date_start:
        users = users.filter(date_joined__gte=date_start)

    date_end = request.GET.get('end_time', '')
    if date_end:
        users = users.filter(date_joined__lte=date_end)

    for user in users:
        user.date_joined = localtime(user.date_joined, ZoneInfo("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M')
    return render(request, 'admin_user.html', {'users': users})


def admin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, f"用户 {user.username} 已删除！")
    return redirect('admin_user')


def admin_edit_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password', '')

        # 更新用户信息
        user.username = username
        user.email = email
        if password:
            user.set_password(password)  # 更新密码
        user.save()

        messages.success(request, f"用户 {username} 信息已更新！")
        return redirect('admin_user')
    return redirect('admin_user')


def admin_post(request):
    query_post_author = request.GET.get('query_post_author', '')
    query_post_content = request.GET.get('query_post_content', '')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')

    # 基本的筛选条件
    posts = Post.objects.all()
    if query_post_author:
        posts = posts.filter(author__username__icontains=query_post_author)
    if query_post_content:
        posts = posts.filter(content__icontains=query_post_content)

    # 根据时间筛选
    if start_time:
        start_datetime = datetime.strptime(start_time, '%Y-%m-%d')
        posts = posts.filter(created_at__gte=start_datetime)
    if end_time:
        end_datetime = datetime.strptime(end_time, '%Y-%m-%d')
        posts = posts.filter(created_at__lte=end_datetime)

    for post in posts:
        post.created_at = localtime(post.created_at, ZoneInfo("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M')

    return render(request, 'admin_post.html', {'posts': posts})


def admin_delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    messages.success(request, f"帖子已删除！")
    return redirect('admin_post')


def admin_review(request):
    query_user_name = request.GET.get('query_user_name', '')
    reviews = Review.objects.all()

    if query_user_name:
        reviews = reviews.filter(user__username__icontains=query_user_name)

    for review in reviews:
        review.created_at = localtime(review.created_at, ZoneInfo("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M')

    return render(request, 'admin_review.html', {'reviews': reviews})


def logout_view(request):
    logout(request)
    return redirect('main_page')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']

        # 验证逻辑
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在，请选择其他用户名')
        elif User.objects.filter(email=email).exists():
            messages.error(request, '邮箱已被注册，请使用其他邮箱')
        elif password != password_confirm:
            messages.error(request, '两次输入的密码不一致')
        else:
            # 注册用户
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                login(request, user)  # 自动登录
                messages.success(request, '注册成功，欢迎您！')
                return redirect('main_page')
            except Exception as e:
                # 捕获意外错误并提示
                messages.error(request, f'注册失败，请稍后重试: {str(e)}')

    # 如果是 GET 请求或者验证失败，渲染注册页面
    return render(request, 'register_page.html')


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    post.created_at = localtime(post.created_at, ZoneInfo("Asia/Shanghai")).strftime('%Y-%m-%d %H:%M')
    post.content = markdown.markdown(post.content)  # 将Markdown转换为HTML

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
    if not request.user.is_authenticated:
        return render(request, 'login_required_page.html')
    user = User.objects.get(id=user_id)
    current_user = request.user

    if user is None or user.is_active is False:
        return render(request, 'no_such_user.html')

    is_blocked = Blocks.objects.filter(user=user, blocked_user=current_user)
    if is_blocked:
        return render(request, 'blocked.html', {'user': user, 'current_user': current_user})

    posts = Post.objects.filter(author=user)

    # 将每个帖子和对应的用户名打包成元组
    posts_with_username = [(post, post.author.username) for post in posts]

    followers_count = Follow.objects.filter(followee=user).count()
    followees_count = Follow.objects.filter(follower=user).count()

    is_following = Follow.objects.filter(follower=current_user, followee=user).exists()

    following_users = Follow.objects.filter(follower=user)
    following_usernames = [follow.followee for follow in following_users]
    followers_users = Follow.objects.filter(followee=user)
    followers_usernames = [follow.follower for follow in followers_users]

    return render(request, 'user_main_page.html', {
        'user': user,  # 目标用户
        'posts': posts_with_username,  # 帖子列表和用户名的元组
        'followers_count': followers_count,  # 粉丝数
        'followees_count': followees_count,  # 关注数
        'is_following': is_following,  # 当前用户是否关注目标用户
        'following_usernames': following_usernames,  # 当前用户关注的用户
        'followers_usernames': followers_usernames,  # 当前用户的粉丝
    })


def follower_page(request, user_id):
    user = User.objects.get(id=user_id)
    followers = Follow.objects.filter(following=user)
    return render(request, 'follower_page.html', {'user': user, 'followers': followers})


def message_page(request):
    user = request.user
    private_messages = Messages.objects.filter(receiver_id=user.id)
    return render(request, 'message_page.html', {'user': user, 'messages': private_messages})


@login_required
def follow_user(request, user_id):
    followee = get_object_or_404(User, id=user_id)
    follower = request.user

    # 检查是否试图关注自己
    if follower == followee:
        messages.error(request, "你不能关注自己！")
        return redirect('user_main_page', user_id=user_id)

    # 如果没有关注过该用户，则创建关注关系
    if not Follow.objects.filter(follower=follower, followee=followee).exists():
        Follow.objects.create(follower=follower, followee=followee)
        messages.success(request, f"你已成功关注 {followee.username}")

    return redirect('user_main_page', user_id=user_id)


@login_required
def unfollow_user(request, user_id):
    followee = get_object_or_404(User, id=user_id)
    follower = request.user

    Follow.objects.filter(follower=follower, followee=followee).delete()

    return redirect('user_main_page', user_id=user_id)


# 确保用户已登录
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # 检查是否是帖子作者或者管理员
    if post.author != request.user and not request.user.is_staff:
        return redirect('post_detail', post_id=post.id)  # 如果不是作者或管理员，跳转回帖子详情页面

    if request.method == 'POST':
        post.delete()  # 删除帖子
        return redirect('main_page')  # 删除后跳转到主页（或其他你需要跳转的页面）

    return render(request, 'confirm_delete.html', {'post': post})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # 确保只有帖子作者或管理员能修改帖子
    if post.author != request.user and not request.user.is_staff:
        return redirect('post_detail', post_id=post.id)  # 如果不是作者或管理员，跳转回帖子详情页面

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()  # 保存修改后的帖子
            return redirect('post_detail', post_id=post.id)  # 修改后跳转到帖子详情页面
    else:
        form = PostForm(instance=post)  # 在GET请求时，加载当前帖子的内容到表单

    return render(request, 'edit_post.html', {'form': form, 'post': post})


def add_server(request, redirect_to, **kwargs):
    user = request.user
    type_of_post = request.POST.get('type')
    if type_of_post == 'create_server':
        # create a server
        name = request.POST.get('name')
        server = create_server(server_name=name, owner=user)
        return redirect(redirect_to, **kwargs)
    elif type_of_post == 'join_server':
        # join a server
        server_id = request.POST.get('addr')
        err, msg = join_server(server_id, user)
        if err == ERROR_SECRET_SERVER:
            messages.error(request, "This is a secret server, you need a password to join")
        elif err == ERROR_ALREADY_IN_SERVER:
            messages.error(request, "You are already in this server")
        elif err == ERROR_BLOCKED_BY_SERVER_OWNER:
            messages.error(request, "You are blocked by the server owner")
        elif err == SUCCESS:
            pass
        return redirect(redirect_to, **kwargs)
    elif type_of_post == 'edit_server':
        # edit a server
        modify_server_id = request.POST.get('modify_server_id')
        name = request.POST.get('name')
        server = Server.objects.get(id=modify_server_id)
        server.name = name
        server.save()
        return redirect(redirect_to, **kwargs)
    elif type_of_post == 'delete_server':
        # delete a server
        delete_server_id = request.POST.get('delete_server_id')
        server = Server.objects.get(id=delete_server_id)
        server.delete()
        server.save()
        if str(delete_server_id) == str(kwargs.get('server_id')):
            return redirect('public_chat_room')
        return redirect(redirect_to, **kwargs)


def add_channel(request, redirect_to, **kwargs):
    user = request.user
    type_of_post = request.POST.get('type')
    server_id = kwargs.get('server_id')
    server = Server.objects.get(id=server_id)
    if user != server.owner:
        messages.error(request, "You are not allowed to edit this server")
        return redirect(redirect_to, **kwargs)
    if type_of_post == 'add_channel':
        # create a channel
        name = request.POST.get('name')
        channel = create_channel(channel_name=name, server=server, current_user=user)
        return redirect(redirect_to, **kwargs)
    elif type_of_post == 'delete_channel':
        # delete a channel
        channels = get_channels_from_server(server)
        if len(channels) == 1:
            messages.error(request, "You can't delete the last channel")
            return redirect(redirect_to, **kwargs)
        delete_channel_id = request.POST.get('delete_channel_id')
        channel = Channel.objects.get(id=delete_channel_id)
        channel.delete()
        channel.save()
        ServerChannel.objects.filter(server=server, channel=channel).delete()

        channels = get_channels_from_server(server)
        if str(delete_channel_id) == str(kwargs.get('channel_id')):
            kwargs['channel_id'] = channels[0].id
        return redirect(redirect_to, **kwargs)
    else:
        # modify a channel
        modify_channel_id = request.POST.get('modify_channel_id')
        name = request.POST.get('name')
        channel = Channel.objects.get(id=modify_channel_id)
        channel.name = name
        channel.save()
        return redirect(redirect_to, **kwargs)


@login_required
def public_chat_room(request):
    # create a server or join a server
    user = request.user
    context = {}
    if request.method == 'POST':
        type_of_post = request.POST.get('type')
        if ("edit" in type_of_post) or ("delete" in type_of_post):
            changed_server_id = request.POST.get('modify_server_id' if "edit" in type_of_post else 'delete_server_id')
            if user != Server.objects.get(id=changed_server_id).owner:
                messages.error(request, "You are not allowed to edit or delete this server")
                return redirect('public_chat_room')

        if "server" in type_of_post:
            return add_server(request, 'public_chat_room')

    context['server_list'] = get_server_list(user=user)
    return render(request, 'public_chat_room.html', context=context)


@login_required
def public_chat_room_in_server(request, server_id):
    if request.method == 'POST':
        type_of_post = request.POST.get('type')
        if "server" in type_of_post:
            return add_server(request, 'public_chat_room_in_server', server_id=server_id)
        if "channel" in type_of_post:
            return add_channel(request, 'public_chat_room_in_server', server_id=server_id)
    user = request.user
    context = {}
    server = Server.objects.get(id=server_id)
    context['server'] = server
    context['channel_list'] = get_channels_from_server(server)
    context['server_list'] = get_server_list(user=user)
    return render(request, 'server.html', context)


@login_required
def channel(request, server_id, channel_id):
    if request.method == 'POST':
        type_of_post = request.POST.get('type')
        if "server" in type_of_post:
            return add_server(request, 'channel', server_id=server_id, channel_id=channel_id)
        if "channel" in type_of_post:
            return add_channel(request, 'channel', server_id=server_id, channel_id=channel_id)
        pass
    user = request.user
    server = Server.objects.get(id=server_id)
    channel = Channel.objects.get(id=channel_id)
    history = get_channel_history(channel)
    context = {
        'server': server,
        'user': user,
        'channel': channel,
        'channel_list': get_channels_from_server(server=server),
        'server_list': get_server_list(user=user),
        'history': history
    }
    return render(request, 'channel.html', context)


@login_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('inbox')
    else:
        form = MessageForm()  # 为 GET 请求初始化表单
    return render(request, 'send_message.html', {'form': form})


@login_required
def inbox(request):
    messages = Messages.objects.filter(receiver=request.user).order_by('-time')
    return render(request, 'inbox.html', {'messages': messages})


@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Messages, id=message_id, receiver=request.user)
    rendered_content = markdown.markdown(message.content)
    return render(request, 'message_detail.html', {'message': message, 'rendered_content': rendered_content})


@login_required
def chat_list(request):
    user = request.user

    # 获取每个对话中最后一条消息的时间戳
    latest_messages = (
        PrivateMessage.objects.filter(
            Q(sender=user) | Q(receiver=user)
        )
        .values('sender', 'receiver')
        .annotate(latest_timestamp=Max('timestamp'))
    )

    # 获取每个对话的最后一条消息
    conversations = []
    M = {}
    for msg in latest_messages:
        last_message = PrivateMessage.objects.filter(
            Q(sender=msg['sender'], receiver=user) | Q(sender=user, receiver=msg['receiver']),
            timestamp=msg['latest_timestamp']
        ).first()
        sender_id = last_message.sender.id
        receiver_id = last_message.receiver.id
        user_id1 = min(sender_id, receiver_id)
        user_id2 = max(sender_id, receiver_id)
        print(user_id1, user_id2)
        mark = f"{user_id1}:{user_id2}"
        last_message = {
            'content': last_message.content,
            'target': last_message.receiver if last_message.sender == user else last_message.sender,
            'sender': last_message.sender,
            'receiver': last_message.receiver,
            'timestamp': localtime(last_message.timestamp, ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M')
        }
        if M.get(mark) is None:
            M[mark] = last_message
        elif M.get(mark)['timestamp'] < last_message['timestamp']:
            M[mark] = last_message
    for key, value in M.items():
        conversations.append(value)
    # 按照最后一条消息的时间戳倒序排列
    conversations = sorted(conversations, key=lambda x: x['timestamp'], reverse=True)

    return render(request, 'chat_list.html', {'conversations': conversations})


# views.py
@login_required
def chat_detail(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    queryset = PrivateMessage.objects.filter(
        models.Q(sender=request.user, receiver=other_user) |
        models.Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')

    messages = [
        {
            'content': message.content,
            'sender': message.sender,
            'receiver': message.receiver,
            'timestamp': localtime(message.timestamp, ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M')
        }
        for message in queryset
    ]

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            PrivateMessage.objects.create(sender=request.user, receiver=other_user, content=content)
        return redirect('chat_detail', user_id=other_user.id)

    return render(request, 'chat_detail.html', {'messages': messages, 'other_user': other_user})
