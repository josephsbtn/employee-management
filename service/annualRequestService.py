from repo.annualRequestRepo import AnnualRequestRepo
from validation.annualRequestschema import AnnualRequestSchema, reviewerSchema
from repo.EmployeeRepo import EmployeeRepo
from validation.employeeSchema import EmployeeSchema
from repo.historyRepo import HistoryRepo
from validation.historySchema import HistorySchema
from marshmallow import ValidationError
import pendulum
import random

class AnnualRequestService:
    """
    Service class untuk mengelola permintaan cuti tahunan (annual leave request).
    
    Class ini menangani operasi CRUD dan business logic terkait permintaan cuti tahunan,
    termasuk validasi tanggal, approval workflow, dan pencatatan history.
    
    Attributes:
        employeeRepo (EmployeeRepo): Repository untuk operasi data employee
        annualRequestRepo (AnnualRequestRepo): Repository untuk operasi data annual request
        employeeValidation (EmployeeSchema): Schema validasi untuk data employee
    """
    
    def __init__(self):
        self.employeeRepo = EmployeeRepo()
        self.annualRequestRepo = AnnualRequestRepo()
        self.employeeValidation = EmployeeSchema()
        self.historyRepo = HistoryRepo()
        self.historySchema = HistorySchema()
        
    def checkDateRange(self, start, end, employeeId):
        """
        Validasi rentang tanggal cuti dan ketersediaan saldo cuti tahunan.

        Method ini melakukan validasi terhadap tanggal mulai dan tanggal akhir cuti,
        memastikan tanggal tidak di masa lalu, tanggal mulai tidak lebih besar dari
        tanggal akhir, dan durasi cuti tidak melebihi saldo cuti yang tersedia.

        Args:
            start (str|date): Tanggal mulai cuti
            end (str|date): Tanggal akhir cuti
            annualLeaveBalance (int): Saldo cuti tahunan yang tersedia
            employeeId (str): ID employee untuk pengecekan overlap

        Returns:
            dict: Dictionary berisi:
                - status (bool): Status validasi (True jika valid)
                - message (str): Pesan error jika tidak valid
                - data (str|int): Data tambahan (tanggal sekarang atau selisih hari)
                - days (int): Jumlah hari cuti jika valid

        Example:
            checkDateRange("2024-01-15", "2024-01-20", 10, "EMP001")
            {'status': True, 'days': 6}
        """
        try:
            if isinstance(start, str):
                start = pendulum.parse(start, tz="Asia/Jakarta").date()
            if isinstance(end, str):
                end = pendulum.parse(end, tz="Asia/Jakarta").date()
            now = pendulum.now(tz="Asia/Jakarta").date()

            print(f"[START]{start} - [END]{end} - [NOW]{now}")

            if start < now:
                return {
                    "status": False, 
                    "message": "Start date cannot be in the past", 
                }

            if end < now:
                return {
                    "status": False, 
                    "message": "End date cannot be in the past", 
                }

            if start > end:
                return {
                    "status": False, 
                    "message": "Start date cannot be after end date", 
                }

            days = (end - start).days + 1
            print("[DAYS]", days)

            employeeRequests = self.annualRequestRepo.getAllData(
                query={"employeeId": employeeId}
            )

            if employeeRequests:
                for request in employeeRequests:
                    if request["status"] not in ["pending", "approved"]:
                        continue
                    reqStart = pendulum.parse(str(request["startDate"]), tz="Asia/Jakarta").date()
                    reqEnd = pendulum.parse(str(request["endDate"]), tz="Asia/Jakarta").date()

                    if (reqStart <= start <= reqEnd or 
                        reqStart <= end <= reqEnd or
                        start <= reqStart and end >= reqEnd):
                        return {
                            "status": False, 
                            "message": f"The date range overlaps with a previous request ({reqStart.strftime('%d-%m-%Y')} to {reqEnd.strftime('%d-%m-%Y')}).",
                        }

            return {"status": True, "days": days}
        except Exception as e:
            print("[ERROR CHECK DATE RANGE]",e)
            return {"status": False, "message": str(e)}
        
        
    def makeHistory(self, data):
        """
        Membuat record history untuk aktivitas terkait cuti.
        
        Method ini mencatat semua aktivitas penting terkait permintaan cuti
        
        Args:
            data (dict): Data history yang berisi:
                - employeeId (str): ID employee yang melakukan aksi
                - employeeName (str): Nama employee
                - description (str): Deskripsi aktivitas
                - type (str): Tipe history (contoh: "leave")
                
        Returns:
            dict: Dictionary berisi:
                - status (bool): Status operasi
                - message (str): Pesan hasil operasi
                
        Raises:
            ValidationError: Jika data tidak valid menurut HistorySchema
            Exception: Jika terjadi error saat insert data
            
        Example:
            >>> makeHistory({
            ...     "employeeId": "EMP001",
            ...     "employeeName": "John Doe",
            ...     "description": "Annual request created",
            ...     "type": "leave"
            ... })
            {'status': True, 'message': 'Data inserted successfully'}
        """
        try:
            data["_id"] = "HIS_" + str(random.randint(10, 99)) +pendulum.now(tz="Asia/Jakarta").strftime("%Y%m%d%H%M%S")
            data = self.historySchema.load(data)
            res = self.historyRepo.insertData(validateData=data)
            if not res.acknowledged:
                result = {"status": False, "message": "Failed to insert data"}
                return result
            return {"status": True, "message": "Data inserted successfully"}
        except ValidationError as e:
            raise ValidationError(e)
        except Exception as e:
            raise Exception(f"Failed to insert data {e}")
        
    def dataReviewer(self,currentUser, note):
        """
        Membuat data reviewer untuk proses approval atau rejection.
        
        Method ini menyiapkan informasi reviewer yang akan disimpan bersama
        dengan status approval/rejection dari permintaan cuti.
        
        Args:
            currentUser (dict): Data user yang melakukan review, berisi:
                - _id (str): ID employee reviewer
                - name (str): Nama reviewer
            note (str): Catatan dari reviewer
            
        Returns:
            dict: Dictionary berisi:
                - status (bool): Status operasi
                - data (dict): Data reviewer yang sudah divalidasi dengan schema
                
        Raises:
            Exception: Jika terjadi error saat mengambil atau memproses data
            
        Example:
            >>> dataReviewer(
            ...     {"_id": "EMP001", "name": "Manager"},
            ...     "Approved with conditions"
            ... )
            {'status': True, 'data': {...}}
        """
        try:
            employee = self.employeeRepo.getData(id=currentUser["_id"])
            payload = {
                "employeeId": employee["_id"],
                "name": employee["name"],
                "timeReviewed" : pendulum.now(tz="Asia/Jakarta"),
                "note": note
            }
            data = reviewerSchema().load(payload)
            
            return {"status": True, "data": data}
        except Exception as e:
            raise Exception(f"Failed to get data {e}")
    
    def createAnnualRequest(self, data, currentUser):
        """
        Membuat permintaan cuti tahunan baru.

        Method ini menangani pembuatan permintaan cuti baru, termasuk validasi
        tanggal, pengurangan saldo cuti (jika tipe annual), dan pencatatan history.

        Args:
            data (dict): Data permintaan cuti berisi:
                - employeeId (str): ID employee yang mengajukan cuti
                - startDate (str): Tanggal mulai cuti
                - endDate (str): Tanggal akhir cuti
                - type (str): Tipe cuti (annual, sick, etc.)
                - reason (str): Alasan cuti
            currentUser (dict): Data user yang membuat request berisi:
                - _id (str): ID user
                - name (str): Nama user

        Returns:
            dict: Dictionary berisi:
                - status (bool): Status operasi
                - message (str): Pesan hasil operasi
                - data (dict, optional): Data tambahan jika ada

        Raises:
            ValueError: Jika validasi tanggal gagal
            ValidationError: Jika data tidak sesuai dengan AnnualRequestSchema
            Exception: Jika terjadi error saat insert data

        Example:
            >>> createAnnualRequest(
            ...     {
            ...         "employeeId": "EMP001",
            ...         "startDate": "2024-01-15",
            ...         "endDate": "2024-01-20",
            ...         "type": "annual",
            ...         "reason": "Family vacation"
            ...     },
            ...     {"_id": "EMP001", "name": "John Doe"}
            ... )
            {'status': True, 'message': 'Annual leave request created successfully'}
        """
        try:
            data["_id"] = "ANR_" + str(random.randint(10, 99)) + pendulum.now(tz="Asia/Jakarta").strftime("%Y%m%d%H%M%S")

            # Ambil data employee
            employee = self.employeeRepo.getData(id=data["employeeId"])
            print("EMPLOYEE: ", employee)
            if not employee:
                return {
                    "status": False, 
                    "message": "Employee not found"
                }


            dateValidation = self.checkDateRange(
                start=data["startDate"], 
                end=data["endDate"], 
                employeeId=data["employeeId"]
            )
            if not dateValidation["status"]:
                return {
                    "status": False, 
                    "message": dateValidation["message"],
                }
            print("[date validation]: ", dateValidation )
            data["days"] = dateValidation["days"]
            data["branchId"] = employee["branchId"]
            
            if data["days"] > employee["annualLeaveBalance"] and data["type"] == "annual":
                return {
                    "status": False, 
                    "message": "Insufficient annual leave balance", 
                    "data": dateValidation["days"] - employee["annualLeaveBalance"]
                }


            

            validatedData = AnnualRequestSchema().load(data)
            print("VALIDATED DATA: ", validatedData)
            result = self.annualRequestRepo.insertData(validateData=validatedData)

            if not result.acknowledged:
                return {
                    "status": False, 
                    "message": "Failed to create leave request"
                }

            # Kurangi saldo cuti hanya jika tipe annual
            if validatedData["type"] == "annual":
                new_balance = employee["annualLeaveBalance"] - validatedData["days"]
                update_result = self.employeeRepo.updateData(
                    validateData={"annualLeaveBalance": new_balance}, 
                    id=validatedData["employeeId"]
                )

                if not update_result:
                    # Rollback: hapus request yang baru dibuat
                    self.annualRequestRepo.deleteData(id=validatedData["_id"])
                    return {
                        "status": False, 
                        "message": "Failed to update leave balance"
                    }

            # Catat history
            self.makeHistory({
                "employeeId": currentUser["_id"], 
                "employeeName": currentUser["name"], 
                "description": f"Annual leave request {validatedData['_id']} created successfully", 
                "type": "leave"
            })

            return {
                "status": True, 
                "message": "Annual leave request created successfully",
                "data": {
                    "requestId": validatedData["_id"],
                    "days": validatedData["days"]
                }
            }
        except ValueError as e:
            raise ValueError(e)
        except ValidationError as e:
            raise ValidationError(e)
        except Exception as e:
            raise Exception(f"Failed to insert data {e}")
        
    def listAnnualByEmployee(self, id):
        """
        Mengambil daftar semua permintaan cuti dari seorang employee.
        
        Method ini mengembalikan semua permintaan cuti yang pernah dibuat
        oleh employee tertentu, baik yang masih pending, approved, rejected,
        maupun canceled.
        
        Args:
            id (str): ID employee yang permintaan cutinya akan diambil
            
        Returns:
            dict: Dictionary berisi:
                - status (bool): Status operasi
                - message (str): Pesan jika tidak ada data
                - data (list): List permintaan cuti atau None jika tidak ada
                
        Raises:
            Exception: Jika terjadi error saat mengambil data
            
        Example:
            >>> listAnnualByEmployee("EMP001")
            {
                'status': True,
                'data': [
                    {'_id': 'ANR001', 'startDate': '2024-01-15', ...},
                    {'_id': 'ANR002', 'startDate': '2024-02-10', ...}
                ]
            }
        """
        try:
            print("==============LIST ANNUAL BY EMPLOYEE==============")
            fetch = self.annualRequestRepo.getAllData(query={"employeeId": id})
            print("[DATA FETCH ANNUAL]",fetch)
            data = []
            for annual in fetch:
                dump = AnnualRequestSchema().dump(annual)
                print("[DUMP ANNUAL]",dump)
                data.append(dump)
                
            print("[DATA ANNUAL]",data)
            if not data:
                return {"status": False, "message": "No data found", "data": None}
            return {"status": True, "data": data}
        except Exception as e:
            raise Exception(f"Failed to get data {e}")
        
    def details(self, id):
        """
        Mengambil detail lengkap dari sebuah permintaan cuti.
        
        Method ini mengembalikan informasi lengkap dari permintaan cuti
        termasuk data employee yang mengajukan.
        
        Args:
            id (str): ID permintaan cuti (annual request ID)
            
        Returns:
            dict: Dictionary berisi:
                - status (bool): Status operasi
                - message (str): Pesan jika tidak ada data
                - data (dict): Detail permintaan cuti beserta data employee, atau None
                
        Raises:
            Exception: Jika terjadi error saat mengambil data
            
        Example:
            >>> details("ANR001")
            {
                'status': True,
                'data': {
                    '_id': 'ANR001',
                    'employeeId': 'EMP001',
                    'startDate': '2024-01-15',
                    'employee': {'_id': 'EMP001', 'name': 'John Doe', ...},
                    ...
                }
            }
        """
        try:
            data = self.annualRequestRepo.getData(id=id)
            if not data:
                return {"status": False, "message": "No data found", "data": None}
            dump = AnnualRequestSchema().dump(data)
            employee = self.employeeRepo.getData(id=dump["employeeId"])
            dump["employee"] = self.employeeValidation.dump(employee)
            return {"status": True, "data": dump}
        except Exception as e:
            raise Exception(f"Failed to get data {e}")
        
    def cancelRequest(self, id, currentUser):
        """
        Membatalkan permintaan cuti.
        
        Method ini memungkinkan employee untuk membatalkan permintaan cuti
        yang telah diajukan sebelumnya (biasanya yang masih pending).
        
        Args:
            id (str): ID permintaan cuti yang akan dibatalkan
            currentUser (dict): Data user yang membatalkan request berisi:
                - _id (str): ID user
                - name (str): Nama user
                
        Returns:
            dict: Dictionary berisi:
                - status (bool): Status operasi
                - message (str): Pesan hasil operasi
                
        Raises:
            Exception: Jika terjadi error saat update data
            
        Example:
            >>> cancelRequest("ANR001", {"_id": "EMP001", "name": "John Doe"})
            {'status': True, 'message': 'Data updated successfully'}
        """
        try:
            update = self.annualRequestRepo.updateData(validateData={"status": "canceled"}, id=id)
            if not update.acknowledged:
                return {"status": False, "message": "Failed to update data"}
            self.makeHistory({"employeeId": currentUser["_id"], "employeeName": currentUser["name"], "description": "Leave Annual request canceled successfully " + str(id), "type": "leave"})
            return {"status": True, "message": "Data updated successfully"}
        
        except Exception as e:
            raise Exception(f"Failed to get data {e}")
    
    def rejectRequest(self, id, currentUser, data):
        """
        Menolak permintaan cuti.
        
        Method ini digunakan oleh manager/supervisor untuk menolak permintaan
        cuti dari employee. Informasi reviewer dan catatan penolakan akan
        disimpan bersama dengan status rejection.
        
        Args:
            id (str): ID permintaan cuti yang akan ditolak
            currentUser (dict): Data reviewer yang menolak request berisi:
                - _id (str): ID reviewer
                - name (str): Nama reviewer
            data (dict): Data tambahan berisi:
                - note (str, optional): Catatan alasan penolakan
                
        Returns:
            dict: Dictionary berisi:
                - status (bool): Status operasi
                - message (str): Pesan hasil operasi
                
        Raises:
            Exception: Jika terjadi error saat update data
            
        Example:
            >>> rejectRequest(
            ...     "ANR001",
            ...     {"_id": "MGR001", "name": "Manager"},
            ...     {"note": "Insufficient staff during this period"}
            ... )
            {'status': True, 'message': 'Data updated successfully'}
        """
        try:
            note = data.get("note", "")
            print("[NOTE]", note)
            reviewer = self.dataReviewer(currentUser, note)
            update = self.annualRequestRepo.updateData(validateData={"status": "rejected","reviewer": reviewer["data"]}, id=id)
            if not update.acknowledged:
                return {"status": False, "message": "Failed to update data"}
            self.makeHistory({"employeeId": currentUser["_id"], "employeeName": currentUser["name"], "description": "Leave Annual request rejected successfully " + str(id), "type": "leave"})
            return {"status": True, "message": "Data updated successfully"}
        
        except Exception as e:
            raise Exception(f"Failed to get data {e}")
    
    def approveRequest(self, id, currentUser, data):
        """
        Menyetujui permintaan cuti.
        
        Method ini digunakan oleh manager/supervisor untuk menyetujui permintaan
        cuti dari employee. Jika tipe cuti adalah "annual", saldo cuti employee
        akan dikurangi. Informasi reviewer dan catatan approval akan disimpan.
        
        Args:
            id (str): ID permintaan cuti yang akan disetujui
            currentUser (dict): Data reviewer yang menyetujui request berisi:
                - _id (str): ID reviewer
                - name (str): Nama reviewer
            data (dict): Data tambahan berisi:
                - note (str, optional): Catatan approval
                
        Returns:
            dict: Dictionary berisi:
                - status (bool): Status operasi
                - message (str): Pesan hasil operasi
                
        Raises:
            Exception: Jika terjadi error saat update data
            
        Example:
            >>> approveRequest(
            ...     "ANR001",
            ...     {"_id": "MGR001", "name": "Manager"},
            ...     {"note": "Approved. Enjoy your leave."}
            ... )
            {'status': True, 'message': 'Data updated successfully'}
        """
        try:
            note = data.get("note", "") 
            request = self.details(id=id)
            print("[REQUEST]", request)
            if request["data"]["type"] == "annual":
                self.employeeRepo.updateData(validateData={"annualLeaveBalance": request["employee"]["annualLeaveBalance"] - request["days"]}, id=request["employeeId"])
            reviewer = self.dataReviewer(currentUser, note)
            update = self.annualRequestRepo.updateData(validateData={"status": "approved","reviewer": reviewer["data"]}, id=id)
            if not update.acknowledged:
                return {"status": False, "message": "Failed to update data"}
            self.makeHistory({"employeeId": currentUser["_id"], "employeeName": currentUser["name"], "description": "Leave Annual request approved successfully " + str(id), "type": "leave"})
            return {"status": True, "message": "Data updated successfully"}
        
        except Exception as e:
            raise Exception(f"Failed to get data {e}")
        
    
    def getRequestByBranch(self, currentUser):
        """
        Mengambil semua permintaan cuti dalam satu branch/cabang.
        
        Method ini digunakan oleh manager/supervisor untuk melihat semua
        permintaan cuti dari employee dalam branch yang sama. Berguna untuk
        monitoring dan approval workflow.
        
        Args:
            currentUser (dict): Data user yang request, berisi:
                - branchId (str): ID branch dari user
                
        Returns:
            dict: Dictionary berisi:
                - status (bool): Status operasi
                - message (str): Pesan jika tidak ada data
                - data (list): List permintaan cuti beserta data employee, atau None
                
        Raises:
            Exception: Jika terjadi error saat mengambil data
            
        Example:
            >>> getRequestByBranch({"branchId": "BRN001"})
            {
                'status': True,
                'data': [
                    {
                        '_id': 'ANR001',
                        'employeeId': 'EMP001',
                        'employee': {'_id': 'EMP001', 'name': 'John Doe', ...},
                        ...
                    },
                    ...
                ]
            }
        """
        try:
            fetch = self.annualRequestRepo.getAllData(query={"branchId": currentUser["branchId"]})
            data = []
            for annual in fetch:
                dump = AnnualRequestSchema().dump(annual)
                dump["employee"] = self.employeeValidation.dump(self.employeeRepo.getData(id=dump["employeeId"]))
                data.append(dump)
            if not data:
                return {"status": False, "message": "No data found", "data": None}
            return {"status": True, "data": data}
        except Exception as e:
            raise Exception(f"Failed to get data {e}")