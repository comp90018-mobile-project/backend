from django.urls import path, include
from . import views as api

urlpatterns = [
    path('demo', api.demo_fetch, name="demo fetch")
]