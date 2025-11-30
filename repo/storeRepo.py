from repo.BaseRepo import BaseRepo

class StoreRepo(BaseRepo):
    def __init__(self):
        super().__init__("stores")
        
    # def addProductToStore(self, productID, storeID):
    #     try:
    #         result = self.collection.update_one({"_id": storeID}, {"$push": {"products":{"productsId": productID}}})
    #     except Exception as e:
    #         raise Exception("Failed to add product to store {e}")
    #     return result   
    
    
    def validateCheckIn(self, coordinates, branchId):
        try:
            result = self.collection.find_one({"_id": branchId, "geometry":
                {
                    "$nearSphere": { #spherical law of cosines atau haversine.
                        "$geometry": {
                            "type": "Point",    
                            "coordinates": coordinates
                        },
                        "$maxDistance": 50
                    },
                }})
            print("RESULT VALIDATE CHECK IN",result)
            return result
        except Exception as e:
            raise Exception("Failed to validate check in", e)