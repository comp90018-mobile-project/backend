import json
from bson import ObjectId
from pymongo.collection import Collection


class MongoJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def insert(collection: Collection, document: dict):
    """Ensure the newly inserted document does not contain _id"""
    collection.insert_one(document)
    document["_id"] = json.loads(json.dumps(document["_id"],
                                            cls=MongoJsonEncoder))
    return document
