import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

def get_user_model():
    from app.models import User
    return User


def get_channel_model():
    from app.models import Channel
    return Channel


def get_channel_message_model():
    from app.models import ChannelMessage
    return ChannelMessage


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.user_name = None
        self.user_id = None
        self.room_group_name = None
        self.channel_id = None
        self.server_id = None

    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.server_id = self.scope['url_route']['kwargs']['server_id']
        self.channel_id = self.scope['url_route']['kwargs']['channel_id']
        self.user = await sync_to_async(get_user_model().objects.get)(id=self.user_id)
        self.user_name = self.user.username
        self.room_group_name = f'chat_{self.server_id}_{self.channel_id}'
        self.channel = await sync_to_async(get_channel_model().objects.get)(id=self.channel_id)

        # 加入聊天组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 离开聊天组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 接收 WebSocket 消息
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # 保存消息
        storage_message = await sync_to_async(get_channel_message_model().objects.create)(
            channel_id=self.channel_id,
            user_id=self.user_id,
            content=message
        )

        formatted_time = storage_message.time.strftime('%Y-%m-%d %H:%M:%S')

        # 发送消息到组
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': self.user_id,
                'user_name': self.user_name,
                'time': formatted_time
            }
        )

    # 接收组消息
    async def chat_message(self, event):
        message = event['message']
        user_id = event['user_id']
        user_name = event['user_name']
        time = event['time']

        # 发送消息到 WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user_id': user_id,
            'user_name': user_name,
            'time': time
        }))


class PrivateMessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from channels.db import database_sync_to_async
        from app.models import User
        # 获取目标用户的ID
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.other_user_id = self.scope['url_route']['kwargs']['other_user_id']
        self.other_user = await database_sync_to_async(User.objects.get)(id=self.other_user_id)
        first_id =min(self.user_id, self.other_user_id)
        second_id = max(self.user_id, self.other_user_id)
        self.room_name = f"chat_{first_id}_{second_id}"
        self.room_group_name = f"chat_{self.room_name}"

        # 加入聊天组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 离开聊天组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 接收 WebSocket 消息
    async def receive(self, text_data):
        from channels.db import database_sync_to_async
        from django.utils import timezone
        text_data_json = json.loads(text_data)
        content = text_data_json['content']

        # 保存消息到数据库
        await database_sync_to_async(self.save_message)(content)

        # 广播消息到该用户的聊天房间
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'sender_id': self.scope['user'].id,
                'sender_username': self.scope['user'].username,
                'content': content,
                'timestamp': str(timezone.now())
            }
        )

    # 处理消息广播
    async def chat_message(self, event):
        message = event['content']
        sender_id = event['sender_id']
        timestamp = event['timestamp']
        sender_username = event['sender_username']

        # 发送消息到 WebSocket
        await self.send(text_data=json.dumps({
            'sender_id': sender_id,
            'sender_username': sender_username,
            'content': message,
            'timestamp': timestamp
        }))

    # 保存消息到数据库
    def save_message(self, content):
        from app.models import PrivateMessage
        PrivateMessage.objects.create(
            sender=self.scope['user'],
            receiver=self.other_user,
            content=content
        )