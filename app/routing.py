from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat_room/<int:server_id>/<int:channel_id>/<int:user_id>/', consumers.ChatConsumer.as_asgi()),
    path('ws/chat/<int:user_id>/<int:other_user_id>/', consumers.PrivateMessageConsumer.as_asgi()),
]