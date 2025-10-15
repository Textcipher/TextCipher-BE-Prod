from django.db import models
from django.contrib.auth.models import User
from message.models import IPAddress


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    sender_IP = models.ForeignKey(IPAddress, on_delete=models.CASCADE, blank=True, null=True)
    checked_by_admin = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Contact from {self.name} <{self.email}>"


class Setting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.IntegerField(default=0)

    def __str__(self):
        return f"Setting {self.key}: {self.value}"