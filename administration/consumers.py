import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ArticleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("articles", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("articles", self.channel_name)

    # Handler for sending article updates
    async def article_update(self, event):
        await self.send(text_data=json.dumps(event))
