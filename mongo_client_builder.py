from pymongo import MongoClient
import os

def build_mongo_client():
    return MongoClient(os.getenv('MONGO_HOST'), 27017)
