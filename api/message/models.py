from django.db import models
from django.utils import timezone


class Message(models.Model):
    message_id = models.CharField(max_length=20, unique=True)
    creator_IP = models.GenericIPAddressField()
    creator_session = models.CharField(max_length=255)
    seen_by = models.CharField(max_length=255, blank=True, null=True)
    seen_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        is_expired = self.expires_at < timezone.now()
        return f"Message {self.message_id} from {self.creator_IP} at {self.created_at} (Expired: {is_expired}) - Session: {self.creator_session} - Seen by: {self.seen_by} at {self.seen_at}"

class Content(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='contents')
    content = models.BinaryField()

    def __str__(self):
        return f"Content for Message {self.message.message_id}"


class MessageV2(models.Model):
    message_id = models.CharField(max_length=20, unique=True)
    creator_IP = models.ForeignKey('IPAddress', on_delete=models.CASCADE, related_name='created_messages')
    created_by = models.ForeignKey('Token', on_delete=models.CASCADE, related_name='created_messages')
    seen_IP = models.ForeignKey('IPAddress', on_delete=models.CASCADE, null=True, blank=True, related_name='seen_messages')
    seen_by = models.ForeignKey('Token', on_delete=models.CASCADE, null=True, blank=True, related_name='seen_messages')
    seen_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        is_expired = self.expires_at < timezone.now() if self.expires_at else False
        return f"MessageV2 {self.message_id} from {self.creator_IP} at {self.created_at} (Expired: {is_expired}) - Created by: {self.created_by} - Seen by: {self.seen_by} at {self.seen_at}"

class ContentV2(models.Model):
    message = models.ForeignKey(MessageV2, on_delete=models.CASCADE, related_name='contents')
    content = models.BinaryField()

    def __str__(self):
        return f"ContentV2 for MessageV2 {self.message.message_id}"


class IPAddress(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ip_address

class Token(models.Model):
    token = models.CharField(max_length=22, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token
