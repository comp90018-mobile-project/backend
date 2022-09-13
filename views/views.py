from django.views.decorators.csrf import csrf_exempt
import pymongo
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from . import config
from .encoders import MongoJsonEncoder
import json

# Global definition for database driver connection
client = pymongo.MongoClient(config.MONGO_ADDR)
db = client.COMP90018
collection: pymongo = db["Users"]


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
