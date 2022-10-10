from django.views.decorators.csrf import csrf_exempt
import pymongo
from pymongo.collection import Collection
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.decorators import api_view, renderer_classes
# from rest_framework.renderers import JSONRenderer
from . import config
from .encoders import MongoJsonEncoder, insert
import json
from django.http import HttpRequest, JsonResponse
from bson import ObjectId
import copy
from datetime import datetime
import datetime

# Global definition for database driver connection
client: pymongo.MongoClient = pymongo.MongoClient(config.MONGO_ADDR)
collection: Collection = client.COMP90018.Users
profile_collection: Collection = client.COMP90018.Profile
event_collection: Collection = client.COMP90018.Events


@csrf_exempt
# @api_view(["POST"])
# @renderer_classes([JSONRenderer])
def create_user(request: HttpRequest):
    """Add a new user to the system."""
    data = request.body
    data_dict = json.loads(data.decode("utf-8"))
    username = data_dict["username"]
    password = data_dict["password"]
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
        "health_status": "negative",
        "avatar": config.DEFAULT_AVATAR
    }
    insert(profile_collection, user_profile)
    return JsonResponse(
        data={
            "msg": "success",
            "data": user_profile
        },
    )


@csrf_exempt
# @renderer_classes([JSONRenderer])
def profile(request: HttpRequest):
    """Get user profile"""
    if request.method == "GET":
        username = request.GET.get(key="username")
        possible_result = profile_collection.find_one({"username": username})
        return JsonResponse(
            data={
                "msg": "success",
                "data": json.loads(
                    json.dumps(possible_result, cls=MongoJsonEncoder))
            }
        )
    elif request.method == "POST":
        params = copy.deepcopy(eval(request.body))
        if request.POST:
            params = request.POST
        username: str = params.get("username")
        query: dict = params.get("query")
        query_filter = {"username": username}
        new_values = {"$set": query}
        res = profile_collection.update_one(
            filter=query_filter, update=new_values
        )
        return JsonResponse(
            data={
                "msg": "Update OK",
                "data": []
            }
        )


# @csrf_exempt
# @api_view(["POST"])
# @renderer_classes([JSONRenderer])
# def mark_user_infected(request: HttpRequest):
#     username = request.POST.get(key="username")
#     user_filter = {"username": username}
#     # 将username标记为已被感染
#     profile_collection.update_one(user_filter, {"$set": {
#         "health_status": "positive"}})
#     # 获取这个人最近3天参加过的所有活动
#     user_info = profile_collection.find_one(user_filter)
#     # event history存储所有event id
#     activities = user_info.get("event_history")
#     potential_contacts = []
#     for event_id in activities:
#         event_info = event_collection.find_one({"_id": ObjectId(event_id)})
#         potential_contacts.extend(
#             event_info.get("participants", [])
#         )
#     # 某些人可能参加了多场活动，去重
#     potential_contacts = list(set(potential_contacts))
#     # Potential contacts保存所有人的username


def create_user_test(username,password):
    """Add a new user to the system."""
    collection.insert_one({
        "username": username,
        "password": password
    })
    # Create user profile at the same time
    user_profile = {
        "username": username,
        "nickname": "vv",
        "signature": "A goose on earth",
        "friends": [],
        "event_history": ["event5"],
        "community": [],
        "health_status": "negative"
    }
    insert(profile_collection, user_profile)
    return JsonResponse(
        data={
            "msg": "success",
            "data": user_profile
        },
    )

# create_user_test("u4","04")

#
def mark_user_positive(username):
    possible_result = profile_collection.find_one({"username": username})
    event_history = possible_result.get("event_history")
    tod = datetime.datetime.now()
    d = datetime.timedelta(days=3)
    start_time = tod - d
    # start from this time, users who join the same event with the marked user will get notification
    # start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    # find all close contact
    all_close_contact = []
    for event_name in event_history:
        event = event_collection.find_one({"name":event_name})
        event_time = event.get("created_at")
        print(datetime.datetime.strptime(event_time, "%Y-%m-%d %H:%M:%S"))
        print(type(start_time))
        if datetime.datetime.strptime(event_time, "%Y-%m-%d %H:%M:%S") > start_time:
            all_close_contact += event.get("participants")
    #去重
    all_close_contact = list(set(all_close_contact))
    all_close_contact.remove(username)
    print(all_close_contact)



def test():
    mark_user_positive("u1")

test()