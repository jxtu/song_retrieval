from pymongo import MongoClient


class DB(object):

    def __init__(self, db_name):
        self.client = MongoClient('127.0.0.1', 27017)
        self.db_name = db_name

    def db_insert(self, post, collection_name):
        db = self.client[self.db_name]
        collection = db[collection_name]
        collection.insert_one(post)