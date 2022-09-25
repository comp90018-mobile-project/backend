from django.views.decorators.csrf import csrf_exempt
import pymongo
from pymongo.collection import Collection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from . import config
from .encoders import MongoJsonEncoder, insert
import json
from django.http import HttpRequest

# Global definition for database driver connection
client: pymongo.MongoClient = pymongo.MongoClient(config.MONGO_ADDR)
collection: Collection = client.COMP90018.Users
profile_collection: Collection = client.COMP90018.Profile

@csrf_exempt
@api_view(["GET"])
@renderer_classes([JSONRenderer])
def demo_fetch(request):
    """A demo API"""
    data = collection.find()
    res = []
    for d in data:
        res.append(d)
    res = json.loads(json.dumps(res, cls=MongoJsonEncoder))
    return Response(
        data={
            "code": 200,
            "data": res
        },
        status=status.HTTP_200_OK
    )


@csrf_exempt
@api_view(["POST"])
@renderer_classes([JSONRenderer])
def create_user(request: HttpRequest):
    """Create a new user in the system."""
    if request.POST:
        # Must be post. Other methods will be denied
        username = request.POST.get(key="username")
        password = request.POST.get(key="password")
        if not username or not password:
            return Response(
                data={
                    "msg": "No username or password found",
                    "data": []
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        # Check if this user already exists
        possible_result = collection.find_one({"username": username})
        if possible_result:
            return Response(
                data={
                    "msg": "User already exists",
                    "data": []
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        collection.insert_one({
            "username": username,
            "password": password
        })
        # Create user profile at the same time
        user_profile = {
            "username": username,
            "nickname": "Echo",
            "signature": "A goose on earth",
            "friends": [],
            "event_history": [],
            "community": [],
            "health_status": "negative"
        }
        insert(profile_collection, user_profile)
        return Response(
            data={
                "msg": "success",
                "data": user_profile
            },
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            data={
                "msg": "method is not allowed",
                "data": []
            }, status=status.HTTP_400_BAD_REQUEST
        )
