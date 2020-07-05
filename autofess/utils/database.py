from autofess import config
from pymongo import MongoClient


mongodbClient = MongoClient(config.DATABASE_URL)
db = mongodbClient.datafess

class Datafess:
    def __init__(self, collection):
        self._db = db[collection]

    def put(self, key, value):
        return self._db.insert_one({ "key": key, "value" : value})

    def get(self, key):
        return self._db.find_one({ "key": key })

    def delete(self, key):
        return self._db.delete_one({ "key" : key })
