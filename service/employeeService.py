from repo.EmployeeRepo import EmployeeRepo
from repo.storeRepo import StoreRepo
from service.attendanceService import AttendanceService
from service.storeService import StoreService
from validation.employeeSchema import EmployeeSchema, UpdateEmployeeSchema, CreatedEmployeeSchema
from bcrypt import hashpw, gensalt, checkpw
from utils.jwtHandler import SessionService
import random
from marshmallow import ValidationError
from validation.employeeSchema import LoginSchema
from service.historyService import HistoryService
import pendulum

class EmployeeService():
    """
    Service class untuk mengelola operasi terkait employee (karyawan).
    
    Class ini menyediakan business logic untuk operasi CRUD employee,
    autentikasi, dan manajemen status employee. Termasuk integrasi dengan
    attendance service, store service, dan history service.
    
    Attributes:
        repo (EmployeeRepo): Repository untuk akses data employee
        employeeSchema (EmployeeSchema): Schema validasi untuk data employee
        createdSchema (CreatedEmployeeSchema): Schema validasi untuk employee baru
        updateSchema (UpdateEmployeeSchema): Schema validasi untuk update employee
        attendanceService (AttendanceService): Service untuk attendance management
        branchService (StoreService): Service untuk store/branch management
        repoBranch (StoreRepo): Repository untuk akses data store/branch
    """
    def __init__(self):
        self.repo = EmployeeRepo()
        self.employeeSchema = EmployeeSchema()
        self.createdSchema = CreatedEmployeeSchema()
        self.updateSchema = UpdateEmployeeSchema()
        self.attendanceService = AttendanceService()
        self.branchService = StoreService()
        self.repoBranch = StoreRepo()
    def getAllEmployee(self, branchId = None):
        """
        Mengambil semua data employee dari database.
        
        Method ini mengambil semua employee dan memperkaya data dengan
        informasi branch terkait. Dapat difilter berdasarkan branchId
        untuk mengambil employee dari cabang tertentu.
        
        Args:
            branchId (str, optional): ID branch untuk filter employee.
                Jika None, akan mengambil semua employee. Default None.
        
        Returns:
            dict: Response object dengan struktur:
                {
                    "status": bool,
                    "message": str,
                    "data": list[dict] - List employee dengan struktur:
                        {
                            "_id": str,
                            "name": str,
                            "email": str,
                            "password": str,
                            "status": str,
                            "role": str,
                            "branchId": str,
                            "branch": dict (informasi branch terkait)
                        }
                }
        
        Raises:
            ValidationError: Jika terjadi error saat validasi schema data
            Exception: Jika terjadi error saat mengambil data dari database
        
        Example:
            >>> service = EmployeeService()
            >>> result = service.getAllEmployee()
            >>> print(result["data"][0]["name"])
            'John Doe'
            
            >>> result = service.getAllEmployee(branchId="STR_123")
            >>> print(len(result["data"]))
            5
        """
        try:
            print("UDAH SAMPE SERVICE GET ALL EMPLOYEE")
            if branchId is not None:
                data = self.repo.getAllData(query={"$and": [{"branchId": branchId}, {"role": "employee"}]})
            else:
                data = self.repo.getAllData()
            print("UDAH NGEFETCH DATA EMPLOYEE = ", data)
            result= []
            for emp in data:
                empData = self.employeeSchema.dump(emp)
                if emp["role"] == "employee" or emp["role"] == "manager":
                    branch_id = empData["branchId"] 
                    if branch_id:   
                        empData["branch"] = self.repoBranch.getDataById(branch_id)
                    result.append(empData)
                if emp["role"] == "owner":
                    result.append(empData)
                
            
            res = {"status" : True, "message" : "Data fetched successfully", "data" :result }
            return res
        except ValidationError as e:
            print("VALIDATION ERROR: ", e)
            raise ValidationError(e)
        except Exception as e:
            print("EXCEPTION: ", e)
            raise Exception(f"Failed to get data: {str(e)}")
    
    def getEmployeeById(self, idEmployee):
        """
        Mengambil data employee berdasarkan ID.
        
        Args:
            idEmployee (str): ID employee yang ingin diambil.
        
        Returns:
            dict: Response object dengan struktur:
                {
                    "status": bool,
                    "message": str,
                    "data": dict - Data employee:
                        {
                            "_id": str,
                            "name": str,
                            "email": str,
                            "password": str,
                            "status": str,
                            "role": str,
                            "branchId": str,
                            "salary": float
                        }
                }
        
        Raises:
            Exception: Jika employee tidak ditemukan atau terjadi error database
        
        Example:
            >>> service = EmployeeService()
            >>> result = service.getEmployeeById("EMP_123")
            >>> print(result["data"]["name"])
            'Jane Smith'
        """
        try:
            data = self.repo.getData(id=idEmployee)
            data = self.employeeSchema.dump(data)
            result = {"status" : True, "message" : "Data fetched successfully", "data" : data}
            return result
        except Exception as e:
            raise Exception(f"Failed to get data: {str(e)}")
        
    def newEmployee(self, data, employee):
        """
        Membuat employee baru dan menyimpannya ke database.
        
        Method ini melakukan validasi data, generate ID unik, hash password,
        dan memastikan tidak ada duplikasi email. Juga melakukan pengecekan
        untuk role manager agar setiap branch hanya memiliki satu manager.
        
        Args:
            data (dict): Data employee baru dengan struktur:
                {
                    "name": str,
                    "email": str,
                    "password": str,
                    "status": str,
                    "role": str ("employee" | "manager" | "owner"),
                    "branchId": str,
                    "salary": float
                }
            employee (dict): Data employee yang melakukan operasi (untuk history)
        
        Returns:
            dict: Response object dengan struktur:
                {
                    "status": bool,
                    "message": str,
                    "data": str (inserted_id jika berhasil)
                }
        
        Raises:
            ValidationError: Jika data tidak sesuai schema validasi
            Exception: Jika terjadi error saat insert ke database
        
        Notes:
            - ID employee di-generate dengan format: EMP_[random][timestamp]
            - Password akan di-hash menggunakan bcrypt
            - Email harus unik dalam sistem
            - Setiap branch hanya boleh memiliki satu manager
        
        Example:
            >>> service = EmployeeService()
            >>> new_emp = {
            ...     "name": "John Doe",
            ...     "email": "john@example.com",
            ...     "password": "secret123",
            ...     "role": "employee",
            ...     "branchId": "STR_123",
            ...     "salary": 5000000
            ... }
            >>> result = service.newEmployee(new_emp, current_user)
            >>> print(result["message"])
            'Data inserted successfully'
        """
        try:
            print("[MASUK SERVICE NEW EMPLOYEE]", data)
            id = "EMP_"+str(random.randint(10, 99))+pendulum.now(tz="Asia/Jakarta").strftime("%Y%m%d%H%M%S")
            print("[DATA EMPLOYEE MASUK]", data)
            validateData = self.createdSchema.load(data)
            if validateData["role"] == "manager":
                managers = self.repo.getAllData(query={"role": "manager", "branchId": validateData["branchId"], "status": "active"})
                if len(managers) >= 1:
                    result = {"status": False, "message": "Branch already has 2 manager"}
                    return result
            employees= self.repo.getAllData(query={"branchId": validateData["branchId"], "role": "employee", "status": "active"})
            if len(employees) >= 6:
                result = {"status": False, "message": "Branch already has 6 employees"}
                return result
            print("[VALIDATE NEW EMPLOYEE]", validateData)
            emailUsed = self.repo.getData(query={"email": validateData["email"]})
            
            if emailUsed:
                result = {"status": False, "message": "Email already used"}
                return result
            validateData["_id"] = id
            salt = gensalt()
            validateData["password"] = hashpw(validateData["password"].encode('utf-8'), salt)
            res = self.repo.insertData(validateData)

            if not res.acknowledged:
                result = {"status": False, "message": "Failed to insert data"}
                return result
            
            history = HistoryService().createHistory(data={
                "employeeId": employee["_id"],
                "employeeName": employee["name"],
                "description": f"New employee {validateData['name']} data inserted successfully",
                "type": "employee"
            })  
            if not history["status"]:
                return {"status": False, "message": "Failed to add history"}
            
            result = {"status": True, "message": "Data inserted successfully", "data": res.inserted_id}
            return result
        except ValidationError as e:
            raise ValidationError(e)
        except Exception as e:
            raise Exception(f"Failed to insert data: {str(e)}")
        
    def fireEmployee(self, employee, id):
        """
        Menonaktifkan employee (soft delete).
        
        Mengubah status employee menjadi 'inactive' tanpa menghapus data
        dari database. Operasi ini dapat di-revert dengan activateEmployee.
        
        Args:
            employee (dict): Data employee yang melakukan operasi (untuk history)
            id (str): ID employee yang akan dinonaktifkan
        
        Returns:
            dict: Response object dengan struktur:
                {
                    "status": bool,
                    "message": str
                }
        
        Raises:
            Exception: Jika terjadi error saat update status employee
        
        Example:
            >>> service = EmployeeService()
            >>> result = service.fireEmployee(current_user, "EMP_123")
            >>> print(result["message"])
            'Data Disabled successfully'
        """
        try:
            res = self.repo.updateData(validateData={"status": "inactive", "branchId": ""}, id=id)
            print("[FIRE EMPLOYEE SERVICE] : ", res)
            if not res.acknowledged:
                result = {"status": False, "message": "Failed to inactivate employee"}
                return result
            history = HistoryService().createHistory({
                "employeeId": employee["_id"],
                "employeeName" : employee["name"],
                "description": f"Employee data {id} disabled successfully",
                "type": "employee"
            })
            
            if not history["status"]:
                result = {"status": False, "message": "Failed to add history"}
                return result
            result = {"status": True, "message": "Data Disabled successfully"}
            return result 
        except Exception as e:
            raise Exception(f"Failed to delete data: {str(e)}")
        
    def activateEmployee(self, employee, id):
        """
        Mengaktifkan kembali employee yang sebelumnya dinonaktifkan.
        
        Mengubah status employee dari 'inactive' menjadi 'active'.
        
        Args:
            employee (dict): Data employee yang melakukan operasi (untuk history)
            id (str): ID employee yang akan diaktifkan
        
        Returns:
            dict: Response object dengan struktur:
                {
                    "status": bool,
                    "message": str
                }
        
        Raises:
            Exception: Jika terjadi error saat update status employee
        
        Example:
            >>> service = EmployeeService()
            >>> result = service.activateEmployee(current_user, "EMP_123")
            >>> print(result["message"])
            'Data Disabled successfully'
        """
        try:
            res = self.repo.updateData(validateData={"status": "active"}, id=id)
            print("[activate EMPLOYEE SERVICE] : ", res)
            if not res.acknowledged:
                result = {"status": False, "message": "Failed to inactivate employee"}
                return result
            history = HistoryService().createHistory({
                "employeeId": employee["_id"],
                "employeeName" : employee["name"],
                "description": f"Employee data {id} activated successfully",
                "type": "employee"
            })
            
            if not history["status"]:
                result = {"status": False, "message": "Failed to add history"}
                return result
            result = {"status": True, "message": "Data Disabled successfully"}
            return result 
        except Exception as e:
            raise Exception(f"Failed to delete data: {str(e)}")
    
    def deleteEmployee(self,id, employee):
        """
        Menghapus employee secara permanen dari database (hard delete).
        
        Berbeda dengan fireEmployee yang hanya menonaktifkan, method ini
        akan menghapus data employee secara permanen dari database.
        
        Args:
            id (str): ID employee yang akan dihapus
            employee (dict): Data employee yang melakukan operasi (untuk history)
        
        Returns:
            dict: Response object dengan struktur:
                {
                    "status": bool,
                    "message": str
                }
        
        Raises:
            Exception: Jika terjadi error saat delete employee
        
        Warning:
            Operasi ini bersifat permanen dan tidak dapat di-undo.
            Pertimbangkan menggunakan fireEmployee untuk soft delete.
        
        Example:
            >>> service = EmployeeService()
            >>> result = service.deleteEmployee("EMP_123", current_user)
            >>> print(result["message"])
            'Data deleted successfully'
        """
        try:
            res = self.repo.deleteData(id=id)
            if not res.acknowledged:
                result = {"status": False, "message": "Failed to delete employee"}
                return result
            history = HistoryService().createHistory({
                "employeeId": employee["_id"],
                "employeeName" : employee["name"],
                "description": f"Employee data {id} removed successfully",
                "type": "employee"
            })
            if not history["status"]:
                return {"status": False, "message": "Failed to add history"}
            print("[DELETE EMPLOYEE SERVICE] : ", res)
            result = {"status": True, "message": "Data deleted successfully"}
            return result 
        except Exception as e:
            raise Exception(f"Failed to delete data: {str(e)}")
    
    def login(self, data):
        """
        Proses autentikasi employee menggunakan email dan password.
        
        Method ini melakukan validasi kredensial, pengecekan status akun,
        dan generate JWT token untuk sesi employee yang berhasil login.
        
        Args:
            data (dict): Data login dengan struktur:
                {
                    "email": str,
                    "password": str
                }
        
        Returns:
            dict: Response object dengan struktur:
                - Berhasil:
                    {
                        "status": True,
                        "token": str (JWT token)
                    }
                - Gagal:
                    {
                        "status": False,
                        "message": str (error message)
                    }
        
        Raises:
            ValidationError: Jika data login tidak valid
            Exception: Jika terjadi error saat proses autentikasi
        
        Notes:
            - Password akan diverifikasi menggunakan bcrypt
            - Akun dengan status 'inactive' tidak dapat login
            - Setiap login berhasil akan tercatat di history
        
        Example:
            >>> service = EmployeeService()
            >>> login_data = {
            ...     "email": "john@example.com",
            ...     "password": "secret123"
            ... }
            >>> result = service.login(login_data)
            >>> if result["status"]:
            ...     print(f"Token: {result['token']}")
        """
        try:
            validateData = LoginSchema().load(data)
            if not validateData or not validateData.get('email') or not validateData.get('password'):
                result = {"status": False, "message": "Missing email or password."}
                return result
            
            user = self.repo.getData(query={"email": data["email"]})
            if not user:
                result = {"status": False, "message": "Email not found"}
                return result

            checkPassword = checkpw(data["password"].encode("utf-8"), user["password"])
            if not checkPassword:
                result = {"status": False, "message": "Invalid Password"}
                return result
            
            if user["status"] == "inactive":
                result = {"status": False, "message": "Your account has been disabled"}
                return result

            token = SessionService().createToken(user)
            history = HistoryService().createHistory({
                "employeeId": user["_id"],
                "employeeName": user["name"],
                "description": f"Login successfully",
                "type": "auth"
            })
            if not history["status"]:
                return {"status": False, "message": "Failed to add history"}
            return {"status": True, "token": token}
        except ValidationError as e:
            raise ValidationError(e)
        except Exception as e:
            raise Exception(f"Failed to login: {str(e)}")
        
    def updateEmploye(self, data, idEmployee, employee):
        """
        Mengupdate data employee yang sudah ada.
        
        Method ini melakukan validasi data update dan memastikan business rules
        seperti satu manager per branch tetap terpenuhi.
        
        Args:
            data (dict): Data yang akan diupdate dengan struktur:
                {
                    "name": str (optional),
                    "email": str (optional),
                    "status": str (optional),
                    "role": str (optional),
                    "branchId": str (optional),
                    "salary": float (optional)
                }
            idEmployee (str): ID employee yang akan diupdate
            employee (dict): Data employee yang melakukan operasi (untuk history)
        
        Returns:
            dict: Response object dengan struktur:
                {
                    "status": bool,
                    "message": str
                }
        
        Raises:
            ValidationError: Jika data tidak sesuai schema validasi
            Exception: Jika terjadi error saat update data
        
        Notes:
            - Hanya field yang disertakan yang akan diupdate
            - Validasi manager per branch tetap diterapkan
            - Perubahan akan tercatat di history
        
        Example:
            >>> service = EmployeeService()
            >>> update_data = {
            ...     "name": "John Doe Updated",
            ...     "salary": 6000000
            ... }
            >>> result = service.updateEmploye(update_data, "EMP_123", current_user)
            >>> print(result["message"])
            'Data updated successfully'
        """
        try:
            validateData = self.updateSchema.load(data)
            if validateData["role"] == "manager":
                managers = self.repo.getAllData(query={"role": "manager", "branchId": validateData["branchId"]})
                if len(managers) >= 1:
                    result = {"status": False, "message": "Branch already has a manager"}
                    return result
            res = self.repo.updateData(validateData=validateData, id=idEmployee)
            if not res.acknowledged:
                result = {"status": False, "message": "Data update failed"}
                return result
            history = HistoryService().createHistory({
                "employeeId": employee["_id"],
                "employeeName" : employee["name"],
                "description": f"Employee {validateData['name']} data updated successfully",
                "type": "employee"
            })
            if not history["status"]:
                return {"status": False, "message": "Failed to add history"}
            
            result = {"status": True, "message": "Data updated successfully"}
            return result
        except ValidationError as e:
            raise ValidationError(e)
        except Exception as e:
            raise Exception(f"Failed to update data: {str(e)}")
        
    def employeeProfile(self, employee):
        """
        Mengambil profil lengkap employee beserta informasi branch.
        
        Method ini mengambil data employee lengkap dan memperkayanya dengan
        informasi branch. Untuk owner, akan menampilkan semua branch dan
        total jumlah branch.
        
        Args:
            employee (dict): Data employee dari token/session dengan struktur:
                {
                    "_id": str,
                    "name": str,
                    "role": str,
                    "branchId": str (optional untuk employee/manager)
                }
        
        Returns:
            dict: Response object dengan struktur:
                {
                    "status": bool,
                    "message": str,
                    "data": dict - Profil employee lengkap:
                        {
                            "_id": str,
                            "name": str,
                            "email": str,
                            "role": str,
                            "salaryPerDay": float,
                            "annualLeaveBalance": int,
                            "branchId": str,
                            "status": str,
                            "createdAt": str,
                            "branch": dict/list (detail branch atau list semua branch),
                            "totalStore": int (hanya untuk owner)
                        }
                }
        
        Raises:
            ValidationError: Jika terjadi error saat validasi schema
            Exception: Jika employee tidak ditemukan atau terjadi error
        
        Notes:
            - Untuk role employee/manager: menampilkan detail branch mereka
            - Untuk role owner: menampilkan semua branch dan total jumlahnya
        
        Example:
            >>> service = EmployeeService()
            >>> current_user = {"_id": "EMP_123", "name": "John", "role": "employee"}
            >>> result = service.employeeProfile(current_user)
            >>> print(result["data"]["name"])
            'John Doe'
            >>> print(result["data"]["branch"]["name"])
            'Aventra Salatiga'
        """
        try:
            id = employee["_id"]
            data = self.repo.getData(id=id)
            employee = self.employeeSchema.dump(data)
            if employee is None:
                result = {"status": False, "message": "Data not found"}
                return result
            store = None
            if employee.get("role") != "owner":
                store = self.branchService.getStoreDetails(employee["branchId"])["data"]
            else :
                store = self.branchService.getAllStore()
                totalEmployees = self.repo.getAllData()
                employee["totalStore"] =  len(store["data"])
                employee["totalEmployee"] = len(totalEmployees)-1
            
            if employee["role"] != "employee":
                employee["workDays"] = (pendulum.now("Asia/Jakarta").date() - pendulum.parse(employee["createdAt"], tz="Asia/Jakarta").date()).days
                print("MANAGER WORKDAYS : ",employee["workDays"])
                
            employee["branch"] = store
            return {"status": True, "message": "Data fetched successfully", "data": employee}
        except ValidationError as e:
            raise ValidationError(e)
        except Exception as e:
            raise Exception(f"Failed to get profile: {e}")