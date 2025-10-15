from django.contrib import admin
from .models import Message, Content, IPAddress, Token, MessageV2, ContentV2

admin.site.register(Message)
admin.site.register(Content)
admin.site.register(MessageV2)
admin.site.register(ContentV2)
admin.site.register(IPAddress)
admin.site.register(Token)