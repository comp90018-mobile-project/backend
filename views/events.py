from django.views.decorators.csrf import csrf_exempt
import pymongo
from pymongo.collection import Collection
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.decorators import api_view, renderer_classes
# from rest_framework.renderers import JSONRenderer
# from rest_framework.decorators import api_view
from . import config
from .encoders import MongoJsonEncoder, insert
import json
from django.http import HttpRequest, JsonResponse
import copy
import arrow
from bson import ObjectId
client: pymongo.MongoClient = pymongo.MongoClient(config.MONGO_ADDR)
collection: Collection = client.COMP90018.Users
profile_collection: Collection = client.COMP90018.Profile
event_collection: Collection = client.COMP90018.Events
now = arrow.now(tz="Australia/Melbourne").format("YYYY-MM-DD HH:mm:ss")



@csrf_exempt
# @renderer_classes([JSONRenderer])
def events(request: HttpRequest):
    if request.method == "GET":
        data = event_collection.find()
        res = []
        for d in data:
            res.append(d)
        res = json.loads(json.dumps(res, cls=MongoJsonEncoder))
        return JsonResponse(
            data={
                "msg": "success",
                "data": res
            },
        )
    elif request.method == "PATCH":
        params = copy.deepcopy(eval(request.body))
        event_id: str = params.get("event_id")
        query: dict = params.get("query")
        query_filter = {"_id": ObjectId(event_id)}
        new_values = {"$set": query}
        res = event_collection.update_one(
            filter=query_filter, update=new_values
        )
        return JsonResponse(
            data={
                "msg": "Update OK",
                "data": []
            },
        )
    elif request.method == "POST":
        # params = copy.deepcopy(request.body)
        # if request.POST:
        #     params = request.POST
        # name = params.get("name")
        # organiser = params.get("organiser")
        # preview = params.get("preview")
        # longitude = params.get("longitude")
        # latitude = params.get("latitude")
        # participants = params.get("participants")
        # settings = params.get("settings")
        # images = params.get("images")
        data = request.body
        data_dict = json.loads(data.decode("utf-8"))
        name = data_dict["name"]
        organiser = data_dict["organiser"]
        preview = data_dict["preview"]
        longitude = data_dict["longitude"]
        latitude = data_dict["latitude"]
        participants = data_dict["participants"]
        settings = data_dict["settings"]
        images = data_dict["images"]
        new_event = {
            "name": name,
            "organiser": organiser,
            "preview": preview,
            "longitude": longitude,
            "latitude": latitude,
            "participants": participants,
            "settings": settings,
            "images": images,
            "created_at": now
        }
        # Keep a unique reference to this new event
        insert(
            collection=event_collection,
            document=new_event
        )
        return JsonResponse(
            data={
                "msg": "success",
                "data": new_event
            },
        )

@csrf_exempt
def event_chats(request: HttpRequest):
    params = request.POST
    chat_info = params.get("chat_info")
    event_id: str = params.get("event_id")
    event_collection.update_one(
        {"_id": ObjectId(event_id)},
        {"$set": {"chat": chat_info}}
    )
    """
    [
        {
            _id: 1,
            sender_name: ZIAWANG1,
            time: xxx,
            content: ,
            mention
        }
    ]
    """
    return JsonResponse(
        data={
            "msg": "Update OK",
            "data": []
        }
    )
