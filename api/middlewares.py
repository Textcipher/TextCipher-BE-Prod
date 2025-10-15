from rest_framework import status
from rest_framework.response import Response

class BlockInvalidOriginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_origins = "https://textcipher.com"

    def __call__(self, request):
        origin = request.headers.get('Origin')
        if origin and origin != self.allowed_origins and request.method != 'OPTIONS':
            return Response({"message": "Invalid origin"}, status=status.HTTP_403_FORBIDDEN)
        
        return self.get_response(request)
