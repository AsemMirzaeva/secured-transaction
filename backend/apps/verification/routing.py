from django.urls import re_path
from .consumers import TransactionStatusConsumer

websocket_urlpatterns = [
    re_path(r"^ws/transactions/$", TransactionStatusConsumer.as_asgi()),
]