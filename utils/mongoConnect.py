from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.config import Config
import logging

class mongoConnection :
    def __init__(self):
        self.dbName = Config.DATABASE
        self.URI = Config.MONGO_URI
        self.client = None
        self.db = None
        if self.client is None:
            self.connect()
        
    def connect(self):
        try:
            self.client = MongoClient(self.URI)
            self.client.admin.command("ping")
            self.db = self.client[self.dbName]
            
        except PyMongoError as e:
            print("Failed to connect with client", e)
            logging.error(f"Failed to connect with client {e}")
        except Exception as e:  
            print("Something wrong", e)
            logging.error(f"Something wrong {e}")
            
            
    def getColleciton(self, collection):
        try:
            if self.db is None:
                self.connect()
            collection = self.db[collection]
            return collection
        except Exception as e:
            print("Failed to get Collection", e)
            logging.error(f"Failed to get Collection {e}")
        