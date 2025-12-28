"""
WebSocket consumers for real-time notifications and chat
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time notifications
    """

    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection
        """
        self.user = self.scope['user']

        # Only allow authenticated users
        if self.user.is_anonymous:
            await self.close()
            return

        # Create a unique group name for this user
        self.group_name = f'notifications_{self.user.id}'

        # Join user's notification group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial notification count
        initial_data = await self.get_initial_data()
        await self.send(text_data=json.dumps(initial_data))

    async def disconnect(self, close_code):
        """
        Called when the websocket closes for any reason
        """
        # Leave user's notification group
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """
        Called when we receive a text frame from the client
        """
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'ping':
                # Respond to ping to keep connection alive
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))
            elif action == 'refresh':
                # Send updated notification count
                initial_data = await self.get_initial_data()
                await self.send(text_data=json.dumps(initial_data))
        except json.JSONDecodeError:
            pass

    async def notification_message(self, event):
        """
        Called when a notification is sent to this user's group
        Receive message from group
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))

    async def notification_count(self, event):
        """
        Called when notification count is updated
        """
        await self.send(text_data=json.dumps({
            'type': 'count_update',
            'unread_count': event['unread_count'],
            'unread_messages_count': event.get('unread_messages_count', 0)
        }))

    @database_sync_to_async
    def get_initial_data(self):
        """
        Get initial notification and message counts
        """
        from .models import Notification, Message

        unread_notifications = Notification.objects.filter(
            user=self.user,
            is_read=False
        ).count()

        unread_messages = Message.objects.filter(
            recipient=self.user,
            is_read=False
        ).count()

        # Get recent notifications
        recent_notifications = list(
            Notification.objects.filter(
                user=self.user
            ).order_by('-created_at')[:5].values(
                'id', 'message', 'notification_type', 'is_read', 'created_at'
            )
        )

        # Convert datetime to string
        for notif in recent_notifications:
            notif['created_at'] = notif['created_at'].isoformat()

        return {
            'type': 'initial',
            'unread_count': unread_notifications,
            'unread_messages_count': unread_messages,
            'recent_notifications': recent_notifications
        }


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling 1-on-1 private chat
    """

    async def connect(self):
        """
        Connect to chat room with another user
        """
        self.user = self.scope['user']
        self.other_username = self.scope['url_route']['kwargs']['username']

        # Only allow authenticated users
        if self.user.is_anonymous:
            await self.close()
            return

        # Get other user
        self.other_user = await self.get_user_by_username(self.other_username)
        if not self.other_user:
            await self.close()
            return

        # Create a unique room name (sorted usernames to ensure same room)
        usernames = sorted([self.user.username, self.other_username])
        self.room_name = f'chat_{usernames[0]}_{usernames[1]}'
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send chat history
        history = await self.get_chat_history()
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': history
        }))

    async def disconnect(self, close_code):
        """
        Leave chat room
        """
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """
        Receive message from WebSocket
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'chat_message':
                # Save message to database
                message_obj = await self.save_message(data.get('message'))

                # Broadcast to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': {
                            'id': message_obj['id'],
                            'sender': self.user.username,
                            'content': message_obj['content'],
                            'timestamp': message_obj['timestamp']
                        }
                    }
                )

                # Send notification to other user
                await self.send_chat_notification(message_obj)

            elif message_type == 'typing':
                # Broadcast typing indicator
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'typing_indicator',
                        'username': self.user.username,
                        'is_typing': data.get('is_typing', False)
                    }
                )

        except json.JSONDecodeError:
            pass

    async def chat_message(self, event):
        """
        Receive message from room group and send to WebSocket
        """
        message = event['message']

        # Determine if message is from me or other user
        if message['sender'] == self.user.username:
            message['sender'] = 'me'
        else:
            message['sender'] = 'other'

        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))

    async def typing_indicator(self, event):
        """
        Receive typing indicator from room group
        """
        # Only send to other user (not the one typing)
        if event['username'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'is_typing': event['is_typing']
            }))

    @database_sync_to_async
    def get_user_by_username(self, username):
        """
        Get user by username
        """
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_chat_history(self):
        """
        Get recent chat history between two users
        使用 ChatMessage 模型（即時聊天專用，與 Message 私人訊息分離）
        """
        from .models import ChatMessage

        messages = ChatMessage.objects.filter(
            Q(sender=self.user, recipient=self.other_user) |
            Q(sender=self.other_user, recipient=self.user)
        ).order_by('created_at')[:50]

        history = []
        for msg in messages:
            history.append({
                'id': msg.id,
                'sender': 'me' if msg.sender == self.user else 'other',
                'content': msg.content,
                'timestamp': msg.created_at.isoformat()
            })

        return history

    @database_sync_to_async
    def save_message(self, content):
        """
        Save chat message to database
        使用 ChatMessage 模型（即時聊天專用，與 Message 私人訊息分離）
        """
        from .models import ChatMessage

        message = ChatMessage.objects.create(
            sender=self.user,
            recipient=self.other_user,
            content=content
        )

        return {
            'id': message.id,
            'content': message.content,
            'timestamp': message.created_at.isoformat()
        }

    @database_sync_to_async
    def send_chat_notification(self, message_obj):
        """
        Send notification to other user about new chat message
        使用特殊的 link 格式讓前端知道這是即時聊天通知
        """
        from .utils.notifications import create_notification

        # Get display name (first_name or username)
        display_name = self.user.first_name if self.user.first_name else self.user.username

        create_notification(
            user=self.other_user,
            notification_type='message',
            message=f'{display_name} 向您發送了即時訊息',
            link=f'/blog/member/{self.user.username}/'  # 連結到發送者的個人頁面
        )
