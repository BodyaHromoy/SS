# ss_main/routing.py
from django.urls import path
from .consumers import MyConsumer

websocket_urlpatterns = [
    path('ws/ss_main/', MyConsumer.as_asgi()),
]
