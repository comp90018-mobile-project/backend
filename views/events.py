from zoneinfo import ZoneInfo

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
from datetime import datetime
import datetime

client: pymongo.MongoClient = pymongo.MongoClient(config.MONGO_ADDR)
collection: Collection = client.COMP90018.Users
profile_collection: Collection = client.COMP90018.Profile
event_collection: Collection = client.COMP90018.Events
now = arrow.now(tz="Australia/Melbourne").format("YYYY-MM-DD HH:mm:ss")


@csrf_exempt
def get_event_by_id(request: HttpRequest):
    if request.GET:
        event_id = request.GET.get("event_id")
        event = event_collection.find_one({"_id": ObjectId(event_id)})
        if event:
            return JsonResponse(
                data={
                    "msg": "success",
                    "data": event
                },
                json_dumps_params={"cls": MongoJsonEncoder}
            )
        else:
            return JsonResponse(
                data={
                    "msg": "event not found"
                }
            )


@csrf_exempt
def events(request: HttpRequest):
    if request.method == "GET":
        if request.GET.get("event_id") is not None:
            event_id = request.GET["event_id"]
            if event_id == "undefined":
                return JsonResponse(
                    data={
                        "msg": "error",
                        "data": "ObjectId is undefined"
                    },status=400
                )
            event = event_collection.find_one({"_id": ObjectId(event_id)})
            if event:
                return JsonResponse(
                    data={
                        "msg": "success",
                        "data": json.loads(json.dumps(event, cls=MongoJsonEncoder))
                    }
                )
            else:
                return JsonResponse(
                    data={
                        "msg": "event not found"
                    }
                )
        else:
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
        event = event_collection.find_one({"_id": ObjectId(event_id)})
        organiser = event.get("organiser")  # email
        participants = event.get("participants")  # Array (email)
        event_active = event.get("active")
        if event_active == "ended":
            # update organiser hosted array
            profile_collection.update_one(
                filter={'email': organiser}, update={"$set": {"event_hosted": []}}
            )
            # update participants participated array
            for user_id in participants:
                profile_collection.update_one(
                    filter={'email': user_id},
                    update={"$set": {"event_participated": []}}
                )
        organiser_user = profile_collection.find_one({"email": organiser})


        return JsonResponse(
            data={
                "msg": "Update OK",
                "data": json.loads(
                    json.dumps(organiser_user, cls=MongoJsonEncoder))
            },
        )
    elif request.method == "POST":
        data = request.body
        data_dict = json.loads(data.decode("utf-8"))
        name = data_dict["name"]
        organiser = data_dict["organiser"]  # email
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
            "active": "pending",
            "created_at": now
        }
        # Keep a unique reference to this new event
        insert(
            collection=event_collection,
            document=new_event
        )
        # Append this event to user's event_history
        user = profile_collection.find_one({"email": organiser})
        # Append this event to user's event_hosted
        user_event_hosted = user["event_hosted"]
        user_event_hosted.append(new_event["_id"])
        event_history = user["event_history"]
        # Store ID only in event history
        event_history.append(new_event["_id"])
        profile_collection.update_one(
            filter={"email": organiser},
            update={"$set": {
                "event_history": event_history,
                "event_hosted": user_event_hosted
            }}
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
    return JsonResponse(
        data={
            "msg": "Update OK",
            "data": []
        }
    )

@csrf_exempt
def delete_event(request: HttpRequest):
    if request.method == "POST":
        data = request.body
        data_dict = json.loads(data.decode("utf-8"))
        if data_dict.get("event_id") is not None:
            event_id = data_dict.get("event_id")
            event = event_collection.find_one({"_id": ObjectId(event_id)})
            organiser = event.get("organiser") # email
            participants = event.get("participants") # Array (email)
            # 活动发起人
            organiser_user = profile_collection.find_one({"email": organiser})
            organiser_event_history = organiser_user.get("event_history")
            if event_id in organiser_event_history:
                organiser_event_history.remove(event_id)
            profile_collection.update_one(
                filter={'email': organiser}, update={"$set": {"event_hosted": [], "event_history":organiser_event_history}}
            )
            # 活动参与者
            for user_id in participants:
                user = profile_collection.find_one({"email": user_id})
                user_event_history = user.get("event_history")
                if event_id in user_event_history:
                    user_event_history.remove(event_id)
                profile_collection.update_one(
                    filter={'email': user_id}, update={"$set": {"event_participated": [], "event_history": user_event_history}}
                )

            # 删除event
            event_collection.delete_one({"_id": ObjectId(data_dict.get("event_id"))})
            return JsonResponse(
                data={
                    "msg": "Delete OK",
                    "data": data_dict.get("event_id")
                }
            )
        else:
            # delete all
            event_collection.delete_many({})
            return JsonResponse(
                data={
                    "msg": "Delete All OK",
                    "data": []
                }
            )
