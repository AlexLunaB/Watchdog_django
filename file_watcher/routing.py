
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/file_socket/$', consumers.FileWatcherConsumer.as_asgi()),

]