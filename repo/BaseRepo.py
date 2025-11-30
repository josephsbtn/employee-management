from utils.mongoConnect import mongoConnection
from pymongo.errors import PyMongoError

class BaseRepo:
    def __init__(self ,collection):
        try:
            self.collection = None
            self.setCollection(collection)
        except PyMongoError as e:
            raise PyMongoError("REPO ERROR : Failed to set Collection", e)
        except Exception as e:
            raise Exception("Failed to set Collection", e)
        
        
    def setCollection(self, entity):
        try:
            self.collection = mongoConnection().getColleciton(entity)
            return self.collection
        except PyMongoError as e:
            raise PyMongoError("REPO ERROR : Failed to set Collection", e)
        except Exception as e:
            raise Exception("Failed to set Collection", e)
        
    def insertData(self, validateData, Multi=False):
        try:
            if Multi:
                resultInsert = self.collection.insert_many(validateData)
            else :
                resultInsert = self.collection.insert_one(validateData)
            return resultInsert
        except PyMongoError as e:
            raise PyMongoError("REPO ERROR : Failed to insert data", e)
        except Exception as e:
            raise Exception("REPO ERROR : Failed to insert data", e)
    def getData(self, id=None, query=None):
        try:
            if query != None:
                result =  self.collection.find_one(query)
                print("--------- result ------------", result)
                return result
            result =  self.collection.find_one({"_id": id})
            print("--------- result ------------", result)
            return result
        except PyMongoError as e:
            raise PyMongoError("REPO ERROR : Failed to insert data", e)
        except Exception as e:
            raise Exception("REPO ERROR : Failed to get data in repo", e)
        
    def getAllData(self, query=None):
        try:
            if query != None:
                result = self.collection.find(query)
                return list(result)
            result = self.collection.find({})
            return list(result)
        except PyMongoError as e:
            raise PyMongoError("REPO ERROR : Failed to get data", e)
        except Exception as e:
            raise Exception("REPO ERROR : Failed to get data in repo", e)
            
    def deleteData(self, id=None, multi=False, query=None):
        try:
            if query != None:
                if multi:
                    result = self.collection.delete_many(query)
                    return result
                result = self.collection.delete_one(query)
                return result 
            if multi:
                result = self.collection.delete_many({"_id": id} )
                return result
            else:
                result = self.collection.delete_one({"_id": id})
                return result
            
        except Exception as e:
            print("Failed to delete data", e)
            return False

    
    def updateData(self, validateData=None, id=None, multi=False, query=None, update=None):
        try:
            if validateData and "_id" in validateData:
                validateData.pop("_id")

            if query is not None:
                if multi:
                    result = self.collection.update_many(query, update)
                else:
                    result = self.collection.update_one(query, update)
                return result

            if multi:
                result = self.collection.update_many({"_id": id}, {"$set": validateData})
            else:
                result = self.collection.update_one({"_id": id}, {"$set": validateData})

            return result

        except Exception as e:
            raise Exception(f"Failed to update data: {e}")
                
    def getDataById(self, id):
        try:
            result = self.collection.find_one({"_id": id})
        except Exception as e:
            raise Exception("Failed to get data {e}")
        return result
    