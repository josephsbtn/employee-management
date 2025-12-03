from utils.mongoConnect import mongoConnection
from pymongo.errors import PyMongoError

class BaseRepo:
    """
    =================================================================================
    BASE REPOSITORY - DOKUMENTASI
    =================================================================================

    MODULE: Base Repository untuk Database Operations

    DESKRIPSI:
    Class ini adalah base repository yang menyediakan operasi CRUD dasar untuk 
    semua collection MongoDB. Semua repository lain harus inherit dari class ini.

    FITUR UTAMA:
    - Create: Insert single/multiple documents
    - Read: Get single/multiple documents dengan query
    - Update: Update single/multiple documents
    - Delete: Delete single/multiple documents
    - Error handling untuk PyMongo dan generic exceptions

    METHODS:
    1. setCollection(entity)           → Set MongoDB collection
    2. insertData(data, Multi)         → Insert document(s)
    3. getData(id, query)              → Get single document
    4. getAllData(query)               → Get multiple documents
    5. getDataById(id)                 → Get document by _id
    6. updateData(data, id, query...)  → Update document(s)
    7. deleteData(id, query, multi)    → Delete document(s)

    ERROR HANDLING:
    - PyMongoError: Database-specific errors
    - Exception: Generic Python exceptions
    - Semua errors di-raise untuk handling di service layer

    USAGE EXAMPLE:
    ```python
    from repository.baseRepo import BaseRepo

    class EmployeeRepo(BaseRepo):
        def __init__(self):
            super().__init__("employees")
        
        def getByEmail(self, email):
            return self.getData(query={"email": email})
    ```

    NOTES:
    - Query menggunakan MongoDB query syntax
    - Multi=True untuk operasi batch
    - _id otomatis di-remove saat update untuk menghindari error
    - Semua results dari find() di-convert ke list

    =================================================================================
    """
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
    