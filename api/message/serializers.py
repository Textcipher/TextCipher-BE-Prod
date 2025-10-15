from rest_framework import serializers
from .models import MessageV2

class MessageSerializer(serializers.Serializer):
    content = serializers.CharField(required=True, allow_blank=False)
    expire_after = serializers.IntegerField(required=False, default=5)
