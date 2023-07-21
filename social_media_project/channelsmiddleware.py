# from urllib.parse import parse_qs
# import jwt
# from django.conf import settings
# from channels.auth import AuthMiddlewareStack
# from channels.db import database_sync_to_async
# from rest_framework_simplejwt.tokens import AccessToken

# @database_sync_to_async
# def get_user(validated_token):
    
#     pass
# class JWTAuthMiddleware:
#     """
#     Middleware that authenticates WebSocket connections using JWT tokens.
#     """
#     def __init__(self, inner):
#         self.inner = inner
#     async def __call__(self, scope, receive, send):
        
#         query_params = scope['query_string'].decode()
#         token = parse_qs(query_params)['token'][0]
#         scope["token"] = token
#         decoded_token = AccessToken(token)
#         scope["auth_user"] = decoded_token.payload
#         return await self.inner(scope, receive, send)
    
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async

CustomUser = get_user_model()

class JWTAuthMiddleware(BaseMiddleware):
    """
    Middleware that authenticates WebSocket connections using JWT tokens.
    """

    async def __call__(self, scope, receive, send):
        query_params = parse_qs(scope['query_string'].decode())
        token = query_params.get('token', [None])[0]

        if token:
            try:
                decoded_token = AccessToken(token)
                user_id = decoded_token.payload.get('user_id')
                if user_id:
                    scope['user'] = await self.get_user(user_id)
            except Exception:
                pass

        return await super().__call__(scope, receive, send)

    @staticmethod
    @database_sync_to_async
    def get_user(user_id):
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return None
