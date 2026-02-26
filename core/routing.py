from django.urls import re_path  # <--- THIS WAS MISSING
from . import consumers

websocket_urlpatterns = [
    # Private 1-on-1 Negotiations
    re_path(r'ws/chat/(?P<conversation_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    # WhatsApp-style Trade Groups
    re_path(r'ws/trade_group/(?P<group_id>\d+)/$', consumers.GroupConsumer.as_asgi()),
]