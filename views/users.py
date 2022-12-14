from zoneinfo import ZoneInfo

from django.views.decorators.csrf import csrf_exempt
import pymongo
from pymongo.collection import Collection
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
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
def create_user(request: HttpRequest):
    """Add a new user to the system."""
    data = request.body
    data_dict = json.loads(data.decode("utf-8"))
    email = data_dict["email"]
    username = data_dict["username"]
    password = data_dict["password"]
    collection.insert_one({
        "email": email,
        "password": password
    })
    # Create user profile at the same time
    user_profile = {
        "username": username,
        "email": email,
        "event_participated": [],
        "event_hosted": [],
        "event_history": [],
        "push_token": '',
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
def getAvatars(request: HttpRequest):
    if request.method == "GET":
        email = request.GET.get(key="email")
        res = []
        email_list = email.split(",")
        for email in email_list:
            r = profile_collection.find_one({"email": email})
            res.append(
                r.get("avatar", "")
            )
        return JsonResponse(
            data={
                "msg": "success",
                "data": json.loads(
                    json.dumps(res, cls=MongoJsonEncoder))
            }
        )

@csrf_exempt
def profile(request: HttpRequest):
    """Get user profile"""
    if request.method == "GET":
        email = request.GET.get(key="email")
        possible_result = profile_collection.find_one({"email": email})
        return JsonResponse(
            data={
                "msg": "success",
                "data": json.loads(
                    json.dumps(possible_result, cls=MongoJsonEncoder))
            }
        )
    elif request.method == "POST":
        params = copy.deepcopy(eval(request.body))
        email: str = params.get("email")
        query: dict = params.get("query")
        query_filter = {"email": email}
        new_values = {"$set": query}
        res = profile_collection.update_one(
            filter=query_filter, update=new_values
        )
        newly_updated_user = profile_collection.find_one({"email": email})
        return JsonResponse(
            data={
                "msg": "Update OK",
                "data": json.loads(
                    json.dumps(newly_updated_user, cls=MongoJsonEncoder))
            }
        )


@csrf_exempt
def push(request: HttpRequest):
    if request.method == "POST":
        params = copy.deepcopy(eval(request.body))
        email: str = params.get("email")
        profile_collection.update_one(
            filter={'email': email}, update={"$set": {"health_status": "positive"}}
        )
        possible_result = profile_collection.find_one({"email": email})
        event_participated = possible_result.get("event_participated")
        event_hosted = possible_result.get("event_hosted")
        event_history = possible_result.get("event_history")
        tod = datetime.datetime.now()
        d = datetime.timedelta(days=3)
        start_time = tod - d
        # # start from this time, users who join the same event with the marked user will get notification
        # # start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        # # find all close contact
        all_close_contact = []
        for event_id in event_history + event_participated + event_hosted:
            # event is event_id
            event = event_collection.find_one({"_id": ObjectId(event_id)})
            event: dict
            event_settings: dict = event.get("settings")
            event_time = event_settings.get("start_time")
            participants = event.get("participants")
            event_time = datetime.datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            if event_time > start_time:
                for participant in participants:
                    all_close_contact.append(participant)
        new_values = {"$set": {"health_status": "pending"}}
        all_close_contact = list(set(all_close_contact))
        if email in all_close_contact:
            all_close_contact.remove(email)
        # Push tokens
        messages = []
        for user_email in all_close_contact:
            # filter by close contact email
            filter_close_contact = {"email": user_email}
            # ???????????????
            profile_collection.update_one(
                filter=filter_close_contact, update=new_values
            )
            # ???token
            res = profile_collection.find_one(filter_close_contact)
            token = res.get("push_token", "")
            username = res.get("username", "")
            message = PushMessage(to=token, body=f"Hi, you have been identified as a close contact of a person with confirmed COVID-19.", title="COVID Warning")
            messages.append(message)
        try:
            response = PushClient().publish_multiple(messages)
        except PushServerError as err:
            return JsonResponse(
                data={
                    "msg": "Not OK.",
                    "data": str(err)
                },
                status=400
            )
        return JsonResponse(
            data={
                "msg": "success",
                "data": all_close_contact
            },
            status=200
        )


def create_user_test(username, password):
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
        event = event_collection.find_one({"name": event_name})
        event_time = event.get("created_at")
        print(datetime.datetime.strptime(event_time, "%Y-%m-%d %H:%M:%S"))
        print(type(start_time))
        if datetime.datetime.strptime(event_time, "%Y-%m-%d %H:%M:%S") > start_time:
            all_close_contact += event.get("participants")
    # ??????
    all_close_contact = list(set(all_close_contact))
    all_close_contact.remove(username)
    print(all_close_contact)
