from django.urls import path, include
from . import users as user_api
from . import events as event_api

urlpatterns = [
    path('users', user_api.create_user, name="create user"),
    path('users/profile', user_api.profile, name="get user profile"),
    path('events', event_api.events, name="events api")
]