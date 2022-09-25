from django.urls import path, include
from . import users as api

urlpatterns = [
    path('demo', api.demo_fetch, name="demo fetch"),
    path('users/create', api.create_user, name = "create user")
]