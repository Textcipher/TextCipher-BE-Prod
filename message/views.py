from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema

from cryptography.fernet import Fernet, InvalidToken

from .models import MessageV2, ContentV2, IPAddress, Token
from .serializers import MessageSerializer
from .utils import get_client_ip, create_unique_id, fernet_key_from_unique_id, adding_token_to_response, generate_unique_token

from django.utils import timezone
import base64

INVALID_TOKEN = [None, "", "None", "null", "NULL", "undefined", "UNDEFINED", "N/A", "n/a"]

class MessageView(viewsets.ViewSet):
    @extend_schema(
        request=MessageSerializer,
        responses = {
            201: {"message": "Message created successfully", "id": "string"},
            400: {"message": "Error message describing the issue"}
        }
    )
    def create(self, request):
        ip = get_client_ip(request)
        guest_token = request.COOKIES.get('token')
        if guest_token in INVALID_TOKEN:
            guest_token = generate_unique_token()
        content = request.data.get('content')
        expire_after = request.data.get('expire_after', 5)
        unique_id = create_unique_id()
        secret_key = unique_id[:6]
        message_id = unique_id[6:]
        key = fernet_key_from_unique_id(secret_key)
        
        if not isinstance(content, str) or not isinstance(expire_after, int):
            if not isinstance(content, str):
                return Response({"message": "content must be a string."}, status=status.HTTP_400_BAD_REQUEST)
            if not isinstance(expire_after, int):
                return Response({"message": "expire_after must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        if expire_after < 1:
            return Response({"message": "Expire after must be at least 1 day."}, status=status.HTTP_400_BAD_REQUEST)

        expires_at = timezone.now() + timezone.timedelta(days=expire_after)
 
        if not content:
            return Response({"message": "Content is required."}, status=status.HTTP_400_BAD_REQUEST)    

        fernet = Fernet(key)
        encrypted_content = fernet.encrypt(content.encode())
        
        ip_instance, created = IPAddress.objects.get_or_create(ip_address=ip)
        token_instance, created = Token.objects.get_or_create(token=guest_token)

        message_instance = MessageV2(message_id=message_id, creator_IP=ip_instance, created_by=token_instance, expires_at=expires_at)
        message_instance.save()
        content_instance = ContentV2(message=message_instance, content=encrypted_content)
        content_instance.save()

        response = Response({"message": "Message created successfully", "id": unique_id}, status=status.HTTP_201_CREATED)

        return adding_token_to_response(response, guest_token)

    @extend_schema(
        responses = {
            200: {"message": "Decrypted message content"},
            400: {"message": "Invalid Token."},
            403: {"message": "Message has already been seen."},
            404: {"message": "Message not found."},
            410: {"message": "Message has expired."}
        }
    )
    def retrieve(self, request, pk=None):
        ip = get_client_ip(request)
        secret_key = pk[:6]
        message_id = pk[6:]        
        key = fernet_key_from_unique_id(secret_key)
        f = Fernet(key)
        
        try:
            message_instance = MessageV2.objects.get(message_id=message_id)
            if message_instance.seen_by:
                return Response({"message": "Message has already been seen."}, status=status.HTTP_403_FORBIDDEN)
            else:
                if message_instance.expires_at < timezone.now():
                    try:
                        content_instance = ContentV2.objects.get(message=message_instance)
                        content_instance.delete()
                    except ContentV2.DoesNotExist:
                        pass
                    return Response({"message": "Message has expired."}, status=status.HTTP_410_GONE)

                try:
                    content_instance = ContentV2.objects.get(message=message_instance)
                    token = content_instance.content
                    if isinstance(token, memoryview):
                        token = token.tobytes()
                    elif isinstance(token, bytearray):
                        token = bytes(token)
                    elif isinstance(token, str):
                        token = token.encode("utf-8")
                    
                    guest_token = request.COOKIES.get('token')
                    if guest_token in INVALID_TOKEN:
                        guest_token = generate_unique_token()

                    decrypted_content = f.decrypt(token).decode()
                    ip_instance, created = IPAddress.objects.get_or_create(ip_address=ip)
                    token_instance, created = Token.objects.get_or_create(token=guest_token)

                    message_instance.seen_IP = ip_instance
                    message_instance.seen_by = token_instance
                    message_instance.seen_at = timezone.now()
                    message_instance.expires_at = timezone.now()
                    message_instance.save()
                    content_instance.delete()

                    response = Response({"message": decrypted_content}, status=status.HTTP_200_OK)
                    return adding_token_to_response(response, guest_token)                    
                except ContentV2.DoesNotExist:
                    return Response({"message": "Content not found."}, status=status.HTTP_404_NOT_FOUND)
                except InvalidToken:
                    return Response({"message": "Invalid Token."}, status=status.HTTP_400_BAD_REQUEST)
                
        except MessageV2.DoesNotExist:
            return Response({"message": "Message not found."}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses = {
            200: {"message": "Message id is valid."},
            403: {"message": "Message has already been seen."},
            404: {"message": "Message id is not valid."},
            410: {"message": "Message has expired."}
        }
    )
    @action(detail=True, methods=['post'], url_path='validate')
    def validate(self, request, pk=None):
        guest_token = request.COOKIES.get('token')
        if guest_token in INVALID_TOKEN:
            guest_token = generate_unique_token()
        message_id = pk[6:]
        expired_messages = MessageV2.objects.filter(seen_by__isnull=True, expires_at__lt=timezone.now())
        for expired_message in expired_messages:
            try:
                content_instance = ContentV2.objects.get(message=expired_message)
                content_instance.delete()
            except ContentV2.DoesNotExist:
                pass           
        try:
            message_instance = MessageV2.objects.get(message_id=message_id)
            if message_instance.seen_by:
                return Response({"message": "Message has already been seen"}, status=status.HTTP_403_FORBIDDEN)
            if message_instance.expires_at < timezone.now():
                return Response({"message": "Message has expired"}, status=status.HTTP_410_GONE)

            response = Response({"message": "Message id is valid"}, status=status.HTTP_200_OK)
            return adding_token_to_response(response, guest_token)
        except MessageV2.DoesNotExist:
            return Response({"message": "Message id is not valid"}, status=status.HTTP_404_NOT_FOUND)