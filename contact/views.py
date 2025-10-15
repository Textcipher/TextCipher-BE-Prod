from django.shortcuts import render
from .models import Contact

from drf_spectacular.utils import extend_schema

from .serializers import ContactSerializer

from rest_framework import viewsets, status
from rest_framework.response import Response

from message.utils import get_client_ip
from message.models import IPAddress

class ContactView(viewsets.ViewSet):

    @extend_schema(
        request= ContactSerializer,
        responses= {
            201: ContactSerializer,
            400: {"message": "Error message describing the issue"}
        }
    )
    def create(self, request):
        name = request.data.get("name")
        email = request.data.get("email")
        message = request.data.get("message")
        ip = get_client_ip(request)

        if not(name and email and message):
            return Response({"error":"name, email and message are required"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            ip_instance, created = IPAddress.objects.get_or_create(ip_address=ip)
            contact_instance = Contact(name=name, email=email, message=message, sender_IP=ip_instance)
            contact_instance.save()
            return Response({"message":"Your message has been sent"}, status=status.HTTP_201_CREATED)