"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
# from views.socket_events import sio
import socketio
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from django.core.wsgi import get_wsgi_application
from views.socket_events import sio
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()
# sio = socketio.Server(async_mode='eventlet')
application = socketio.WSGIApp(sio, application)
pywsgi.WSGIServer(('', 8000), application, handler_class=WebSocketHandler).serve_forever()
