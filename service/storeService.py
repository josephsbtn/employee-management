from repo.storeRepo import StoreRepo
from repo.EmployeeRepo import EmployeeRepo
from validation.employeeSchema import EmployeeSchema
from validation.storeSchema import StoreSchema, UpdateStoreSchema, createStoreSchema
from marshmallow import ValidationError
import random
from datetime import datetime
from service.historyService import HistoryService


class StoreService:
    def __init__(self):
        self.repo = StoreRepo()
        self.schema = StoreSchema()
        self.createSchema = createStoreSchema()
        self.updateSchema = UpdateStoreSchema()
        self.employeeRepo = EmployeeRepo()
        self.employeeSchema = EmployeeSchema()
        self.historyService = HistoryService()
        
    def addStore(self, data, employeeId, employeeName ):
        """
        Add a new store to the database.

        Parameters:
        data (dict): The data of the store to be added.
        employeeId (str): The ID of the employee who added the store.
        employeeName (str): The name of the employee who added the store.

        Returns:
        dict: A dictionary containing the status of the operation and the ID of the added store.
        """
        try:
            id = "STR_"+str(random.randint(10, 99))+datetime.now().strftime("%Y%m%d%H%M%S")
            print("[SERVICE ADD STORE : ]" , id )
            data["_id"] = id
            data = self.createSchema.load(data)
            print("[SERVICE ADD STORE : ]" , data )
            store = self.repo.insertData(data)
            storeId = str(store.inserted_id)
            if not storeId:
                result = {"status": False, "message": "Failed to insert data"}
                return result
            
            if not store.acknowledged:
                raise Exception("Failed to add store")
            
            history = self.historyService.createHistory(data={
                "description": "Store added successfully " + str(storeId) +" name "+ str(data["name"]),
                "type": "branch",
                "employeeId": employeeId,
                "employeeName": employeeName
            })
            
            if not history["status"]:
                raise Exception("Failed to add history")
            
            return {"status": True, "message": "Store added successfully", "data": {
                "Store": id,
            }} 
        except ValidationError as e:
            print("VALIDATION ERROR: ", e)
            raise ValidationError(e)
        except Exception as e:
            raise Exception(f"Failed to add store {e}")
        
    def getAllStore(self):
        """
        Get all store data

        Returns:
        dict: A dictionary containing the status of the operation and the data of all stores.
        """
        try:
            data = self.repo.getAllData()
            return {"status": True, "message": "Data fetched successfully", "data": data}
        except Exception as e:
            raise Exception(f"Failed to get data {e}")
    
    def storeDetails(self, id):
        try:
            data = self.repo.getData(id=id)
            data["employees"] = self.employeeRepo.getAllData(query={"storeID": id})
            return {"status": True, "message": "Data fetched successfully", "data": data}
        except Exception as e:
            raise Exception("Failed to get data {e}")
        
    def deleteStore(self, id,  employeeId, employeeName):
        try:
            employee = self.employeeRepo.getAllData(query={"branchId": id})
            print("EMPLOYEE : ", employee)
            if len(employee) > 0 and employee != None:
                employee = self.employeeRepo.deleteData(query={"branchId": id}, multi=True)
            
            store  = self.repo.deleteData(id=id)
            if not store and not employee:
                result = {"status": False, "message": "Failed to delete data"}
                return result
            
            history = self.historyService.createHistory(data={
                "employeeId": employeeId,
                "employeeName": employeeName,
                "description": "Store deleted successfully " + str(id),
                "type": "branch"
            })
            
            if not history["status"]:
                raise Exception("Failed to add history")
            
            return {"status": True, "message": "Data deleted successfully"}
        except Exception as e:
            raise Exception(f"Failed to delete data", e)
    
    def updateStore(self, id, data,  employeeId, employeeName):
        try:
            print("UPDATE SERVICE-----")
            print("[SERVICE DATA]: ", data)
            del data["id"]
            data = self.updateSchema.load(data)
            print("[SERVICE UPDATE STORE : ]" , data )
            res = self.repo.updateData(validateData=data, id=id)
            print("[SERVICE UPDATE STORE RESULT : ]" , res )
            if not res.acknowledged:
                result = {"status": False, "message": "Failed to update data"}
                return result
            
            history = self.historyService.createHistory(data={
                "employeeId": employeeId,
                "employeeName": employeeName,
                "description": "Store updated successfully " + str(id),
                "type": "branch"
            })
            
            if not history["status"]:
                raise Exception("Failed to add history", e)
            
            return {"status": True, "message": "Data updated successfully"}
        except ValidationError as e:
            print("VALIDATION ERROR: ", e)
            raise ValidationError(e)
        except Exception as e:
            raise Exception(f"Failed to update data e")
        
        
    def nonActivateStore(self, id, employee):
        try:
            data = self.repo.updateData(id=id, validateData={"status": "inactive"})
            print("---- NON ACTIVATE STORE SERVICE -----: ", data)
            employees = self.employeeRepo.updateData(query={"branchId": id}, update={"$set": {"status": "inactive", "branchId": None}}, multi=True)
            print("--- NON ACTIVATE EMPLOYEE SERVICE ----: ", employees)
            if not employees.acknowledged:
                result = {"status": False, "message": "Failed to update data"}
                return result
            if not data.acknowledged:
                result = {"status": False, "message": "Failed to update data"}
                return result
            history = self.historyService.createHistory(data={
                "employeeId": employee["_id"],
                "employeeName": employee["name"],
                "type": "branch",
                "description": "Store disabled successfully " + str(id),
            })
            
            if not history["status"]:
                raise Exception("Failed to add history")
            return {"status": True, "message": "Data fetched successfully"}
        except Exception as e:
            raise Exception("Failed to get data ",e)
        
    def ActivateStore(self, id, employee):
        try:
            data = self.repo.updateData(id=id, validateData={"status": "active"})
            print("---- NON ACTIVATE STORE SERVICE -----: ", data)
            if not data.acknowledged:
                result = {"status": False, "message": "Failed to update data"}
                return result
            history = self.historyService.createHistory(data={
                "employeeId": employee["_id"],
                "employeeName": employee["name"],
                "type": "branch",
                "description": "Store disabled successfully " + str(id),
            })
            
            if not history["status"]:
                raise Exception("Failed to add history")
            return {"status": True, "message": "Data fetched successfully"}
        except Exception as e:
            raise Exception("Failed to get data ",e)
        
    def getStoreDetails(self, id):
        try:
            data = self.repo.getData(id=id)
            if data == None:
                return {"status": False, "message": "Data not found"}
            employees = self.employeeRepo.getAllData(query={"branchId": id})
            validate = []
            for emp in employees:
                dump = self.employeeSchema.dump(emp)
                validate.append(dump)
            data["employees"] = validate
            return {"status": True, "message": "Data fetched successfully", "data": data}
        except Exception as e:
            raise Exception(f"Failed to get data {e}")
        
    def getActiveStore(self):
        try:
            data = self.repo.getAllData(query={"status": "active"})
            print("DATA : ", data)
            data = self.schema.dump(data, many=True)
            print("DATA : ", data)
            return {"status": True, "message": "Data fetched successfully", "data": data}
        except Exception as e:
            raise Exception(f"Failed to get data {e}")
        