# ss_main/routing.py
from django.urls import path
from .consumers import MyConsumer, MyReports

websocket_urlpatterns = [
    path('ws/ss_main/', MyConsumer.as_asgi()),
    path('ws/ss_main/reports', MyReports.as_asgi()),
]
