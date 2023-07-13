from urllib.parse import parse_qs
import jwt
from django.conf import settings
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken

@database_sync_to_async
def get_user(validated_token):
    
    pass
class JWTAuthMiddleware:
    """
    Middleware that authenticates WebSocket connections using JWT tokens.
    """
    def __init__(self, inner):
        self.inner = inner
    async def __call__(self, scope, receive, send):
        
        query_params = scope['query_string'].decode()
        token = parse_qs(query_params)['token'][0]
        scope["token"] = token
        decoded_token = AccessToken(token)
        scope["auth_user"] = decoded_token.payload
        return await self.inner(scope, receive, send)