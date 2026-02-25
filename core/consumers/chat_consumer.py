import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from ..models import Product, Message

class SosoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.product_id = self.scope['url_route']['kwargs']['product_id']
        self.room_group_name = f'soso_{self.product_id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'message':
            # Save message and broadcast
            await self.save_message(data['text'])
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_broadcast',
                    'text': data['text'],
                    'user': self.scope['user'].username
                }
            )

        elif action == 'bid':
            # Validate and save bid
            new_bid = float(data['amount'])
            success, updated_price = await self.place_bid(new_bid)
            
            if success:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'bid_broadcast',
                        'amount': updated_price,
                        'user': self.scope['user'].username
                    }
                )

    # --- Broadcast Handlers ---
    async def chat_broadcast(self, event):
        await self.send(text_data=json.dumps(event))

    async def bid_broadcast(self, event):
        await self.send(text_data=json.dumps(event))

    # --- Database Operations ---
    @database_sync_to_async
    def save_message(self, text):
        # We'd fetch the ChatGroup linked to the product here
        product = Product.objects.get(id=self.product_id)
        return Message.objects.create(group=product.chat, user=self.scope['user'], text=text)

    @database_sync_to_async
    def place_bid(self, amount):
        product = Product.objects.get(id=self.product_id)
        if amount > product.highest_bid:
            product.highest_bid = amount
            product.highest_bidder = self.scope['user']
            product.save()
            return True, float(product.highest_bid)
        return False, float(product.highest_bid)