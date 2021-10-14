import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class FileWatcherConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):

        self.group="files"

        await self.channel_layer.group_add(
            group=self.group,
            channel=self.channel_name
        )


        await self.accept()
        # Send message to room group
        await self.channel_layer.group_send(
            self.group,
            {
                'type': 'send_message',
                'message': "Bienvenido al socket"
            }
        )

    async def receive_json(self, content, **kwargs):
        print(content)
        message_type = content.get('type')

    async def echo_message(self, message):
        await self.send_json(message)
        print(self.channel_name)
        await self.channel_layer(
            group=self.group,
            channel=self.channel_name
        )


    # Receive message from room group
    async def send_message(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send_json(content={
            'message': message
        })