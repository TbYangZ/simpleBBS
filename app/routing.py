from django.urls import path
from . import consumers


websocket_urlpatterns = [
    path('ws/chat_room/<int:server_id>/<int:channel_id>/<int:user_id>/', consumers.ChatConsumer.as_asgi()),
]