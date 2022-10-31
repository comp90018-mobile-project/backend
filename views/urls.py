from django.urls import path, include
from . import users as user_api
from . import events as event_api

urlpatterns = [
    path('users', user_api.create_user, name="create user"),
    path('users/profile', user_api.profile, name="get user profile"),
    path('events', event_api.events, name="events api"),
    path('events/delete', event_api.delete_event, name="delete one or more events"),
    path('events/chat', event_api.event_chats, name="chat rooms for one event"),
    path('users/push', user_api.push, name="push notification test")
]
