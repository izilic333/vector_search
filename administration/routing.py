from django.urls import path

from administration.consumers import ArticleConsumer

websocket_urlpatterns = [
    path('ws/administration/', ArticleConsumer.as_asgi()),
]
