import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, Conversation, GroupMessage, TradeGroup

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.room_name}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data['message']
        user = self.scope["user"]

        if user.is_authenticated:
            # Save to DB
            await self.save_chat_message(self.room_name, user, message_text)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_text,
                    'username': user.username
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_chat_message(self, conv_id, user, text):
        return Message.objects.create(conversation_id=conv_id, sender=user, text=text)

class GroupConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.room_group_name = f'trade_group_{self.group_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope["user"]
        
        if user.is_authenticated:
            await self.save_group_message(self.group_id, user, data['message'])
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'group_message',
                    'message': data['message'],
                    'username': user.username
                }
            )

    async def group_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_group_message(self, group_id, user, text):
        return GroupMessage.objects.create(group_id=group_id, sender=user, content=text)