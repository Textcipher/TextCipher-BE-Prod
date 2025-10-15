import uuid
import base64
import os

from datetime import date

from message.models import MessageV2
from contact.models import Setting

from decouple import config
from django.db import transaction
from django.db.models import F

from django.utils import timezone
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def generate_crypto_key():
    key = str(uuid.uuid4().hex[:6])
    return key

def generate_message_unique_id():
    # Create a unique identifier using UUID4 for 8 characters
    month = timezone.now().strftime("%m")
    year = timezone.now().strftime("%Y")[2:]
    unique_code = str(uuid.uuid4().hex[:16])
    code = f"{year}{month}{unique_code}"
    # Check if the unique code is already used
    while MessageV2.objects.filter(message_id=code).exists():
        unique_code = str(uuid.uuid4().hex[:16])
        code = f"{year}{month}{unique_code}"
    return code    
    
def create_unique_id():
    key = generate_crypto_key()
    unique_id = generate_message_unique_id()
    return f"{key}{unique_id}"

def fernet_key_from_unique_id(unique_id):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        salt=unique_id.encode('utf-8'),
        length=32,
        iterations=1_200_000,
    )

    key = base64.urlsafe_b64encode(kdf.derive(unique_id.encode('utf-8')))
    return key


def generate_unique_token() -> str:
    today = date.today()
    year = str(today.year)[2:]
    month = str(today.month).zfill(2)

    with transaction.atomic():
        obj, created = Setting.objects.select_for_update().get_or_create(
            key="visitor",
            defaults={"value": 0},
        )
    if len(str(obj.value)) > 9:
        visitor_id = str(obj.value)[-9:]
    else:
        visitor_id = str(obj.value).zfill(9)
    unique_id = str(uuid.uuid4())[:7]
    token = f"{visitor_id}-{year}{month}-{unique_id}"
    obj.value = F("value") + 1
    obj.save(update_fields=["value"])
    obj.refresh_from_db(fields=["value"])

    return token

def adding_token_to_response(response, token):
    with transaction.atomic():
            obj, created = Setting.objects.select_for_update().get_or_create(
                key="visitor",
                defaults={"value": 0},
            )
            obj.value = F("value") + 1
            obj.save(update_fields=["value"])
            obj.refresh_from_db(fields=["value"])
            visitor_id = obj.value


    response.set_cookie(
        "token",
        token,
        max_age=365 * 24 * 60 * 60,
        httponly=True,
        secure=(config("ENVIRON", default="LOCAL") != "LOCAL"),
        samesite="Lax",          
        path="/",
    )
    return response