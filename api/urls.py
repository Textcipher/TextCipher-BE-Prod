from message.views import MessageView
from contact.views import ContactView
from django.urls import path, include
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'messages', MessageView, basename='message')
router.register(r'contact', ContactView, basename='contact')

urlpatterns = [
    path('', include(router.urls)),
]