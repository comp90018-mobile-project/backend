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
def events(request: HttpRequest):
    if request.method == "GET":
        data = event_collection.find()
        res = []
        for d in data:
            res.append(d)
        res = json.loads(json.dumps(res, cls=MongoJsonEncoder))
        # for event in res:
        #     event_id = event['_id']
        #     s_time = event['settings']['start_time']
        #     s_time = datetime.datetime.strptime(s_time, '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(ZoneInfo('Australia/Melbourne')).strftime('%Y-%m-%d %H:%M:%S')
        #     start_time = datetime.datetime.strptime(s_time, "%Y-%m-%d %H:%M:%S")
        #     duration = event['settings']['duration']
        #     duration_mins = 0
        #     if duration == "30 mins":
        #         duration_mins = 30
        #     elif duration == "1 hour":
        #         duration_mins = 60
        #     elif duration == "1 hour 30 mins":
        #         duration_mins = 90
        #     elif duration == "2 hours":
        #         duration_mins = 120
        #     elif duration == "2 hours 30 mins":
        #         duration_mins = 150
        #     else:
        #         duration_mins = 180
            # d = datetime.timedelta(minutes=duration_mins)
            # end_time = start_time + d
            # if datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S") > end_time:
            #     event_collection.update_one(filter={"_id": ObjectId(event_id)}, update={"$set": {"active": False}})


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
            "active": "false",
            "created_at": now
        }
        # Keep a unique reference to this new event
        insert(
            collection=event_collection,
            document=new_event
        )
        # Append this event to user's event_history
        user = profile_collection.find_one({"email": organiser})
        event_history = user["event_history"]
        # Store ID only in event history
        event_history.append(new_event["_id"])
        profile_collection.update_one(filter={"email": organiser}, update={"$set": {"event_history": event_history}})
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
