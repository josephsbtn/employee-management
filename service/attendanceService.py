from repo.attendanceRepo import AttendanceRepo
from repo.storeRepo import StoreRepo
from repo.shiftsRepo import ShiftsRepo
from repo.EmployeeRepo import EmployeeRepo
from validation.attendanceSchema import ShiftListSchema, EmployeeAttendanceSchema, updateListSchema
from validation.storeSchema import GeometrySchema
from validation.employeeSchema import EmployeeSchema
from marshmallow import ValidationError
from service.historyService import HistoryService
import pendulum
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AttendanceService:
    """
    ===============================================================
    ATTENDANCE SERVICE
    ===============================================================
    Service class untuk mengelola seluruh proses absensi, shift, dan jadwal kerja
    karyawan. Semua validasi dan manipulasi data difokuskan di layer ini
    sebelum diteruskan ke repository.
    
    Class ini menangani:
    - Clock in/out karyawan dengan validasi lokasi
    - Manajemen shift (Day/Night)
    - Penjadwalan karyawan
    - Laporan kehadiran bulanan
    - Validasi waktu dan lokasi absensi

    ===============================================================
    STRUKTUR DATA KOLEKSI `attendance`
    ---------------------------------------------------------------
    {
        "_id": "SHF_2025-10-31_4866",
        "Date": "2025-10-31T00:00:00.000+00:00",
        "branchId": "STR_9820251023235635",
        "employees": [
            {
                "employeeId": "EMP_5720251026183500",
                "shift": "Day",
                "clockIn": null,
                "clockOut": null,
                "status": "absent"
            }
        ],
        "createdAt": "2025-10-31T09:48:33.751+00:00",
        "updatedAt": "2025-10-31T20:20:25.460+00:00"
    }

    ===============================================================
    📦 STRUKTUR DATA KOLEKSI `shifts`
    ---------------------------------------------------------------
    {
        "_id": "SHF_00129102025",
        "shiftName": "Day",
        "shiftStartTime": "07:00:00",
        "shiftEndTime": "15:00:00"
    }

    ===============================================================
    📘 SCHEMA VALIDATION
    ---------------------------------------------------------------
    - ShiftListSchema        → validasi daftar shift harian
    - EmployeeAttendanceSchema → validasi data per karyawan
    - updateListSchema       → validasi update shift
    - GeometrySchema         → validasi lokasi (GeoJSON)
    - EmployeeSchema         → validasi data karyawan
    
    ===============================================================
    Attributes:
        repo (AttendanceRepo): Repository untuk operasi data attendance
        shiftListSchema (ShiftListSchema): Schema validasi daftar shift
        EmploAttendSchema (EmployeeAttendanceSchema): Schema validasi attendance karyawan
        storeRepo (StoreRepo): Repository untuk operasi data store/branch
        shiftsRepo (ShiftsRepo): Repository untuk operasi data shift
        employeeRepo (EmployeeRepo): Repository untuk operasi data employee
        employeeSchema (EmployeeSchema): Schema validasi data employee
        updateShiftSchema (updateListSchema): Schema validasi update shift
    """
    def __init__(self):
        self.repo = AttendanceRepo()
        self.shiftListSchema = ShiftListSchema()
        self.EmploAttendSchema = EmployeeAttendanceSchema()
        self.storeRepo = StoreRepo()
        self.shiftsRepo = ShiftsRepo()
        self.employeeRepo = EmployeeRepo()
        self.employeeSchema = EmployeeSchema()
        self.updateShiftSchema = updateListSchema()

    def getAttendanceByStore(self, storeId, date=None):
        """
        Mengambil data attendance untuk store/branch tertentu pada tanggal spesifik.
        
        Method ini mengembalikan daftar lengkap karyawan yang dijadwalkan beserta
        status kehadiran mereka (present, late, absent) pada tanggal yang ditentukan.
        Data karyawan akan di-populate dengan informasi lengkap dari employee collection.
        
        Args:
            storeId (str): ID store/branch yang akan diambil data attendancenya
            date (str, optional): Tanggal dalam format string (ISO 8601).
                                 Jika None, akan menggunakan tanggal hari ini.
                                 
        Returns:
            dict: Dictionary berisi:
                - status (bool): Status operasi
                - message (str): Pesan hasil operasi
                - data (dict|None): Data attendance termasuk:
                    - _id: ID shift
                    - Date: Tanggal shift
                    - branchId: ID branch
                    - employees: List karyawan dengan detail lengkap
                    
        Raises:
            Exception: Jika terjadi error saat mengambil data
            
        Example:
            >>> getAttendanceByStore("STR_9820251023235635", "2025-10-31")
            {
                'status': True,
                'message': 'Data fetched successfully',
                'data': {
                    '_id': 'SHF_2025-10-31_4866',
                    'Date': '2025-10-31',
                    'employees': [
                        {
                            'employeeId': 'EMP001',
                            'shift': 'Day',
                            'clockIn': '07:05:00',
                            'status': 'present',
                            'employee': {...}
                        }
                    ]
                }
            }
        """
        try:
            date = pendulum.parse(date, tz="UTC")
            data = self.repo.getData(query={"branchId": storeId, "Date": date})
            print("[ATTENDANCE]data = ", data)
            if not data:
                return {"status": False, "message": "No data found", "data": None}
            print("===== get data = ", data)
            
            if not data:
                return {"status": False, "message": "No data found", "data": None}
            
            validated = self.shiftListSchema.dump(data)
            print("validated = ", validated)
            
            
            for emp in validated["employees"]:
                employee = self.employeeRepo.getDataById(id=emp["employeeId"])
                emp["employee"] = self.employeeSchema.dump(employee)
                
            print("validated = ", validated )
            return {
                "status": True, 
                "message": "Data fetched successfully", 
                "data": validated
            }

        except Exception as e:
            raise Exception(f"Failed to get data: {str(e)}")
        
    def employeeClockOut(self, data, employee):
        """
        Proses clock out karyawan dengan validasi lokasi dan waktu.
        
        Method ini menangani proses clock out karyawan dengan melakukan validasi:
        - Karyawan sudah clock in sebelumnya
        - Waktu clock out sudah melewati waktu akhir shift
        - Lokasi clock out berada dalam radius yang diizinkan dari store
        
        Args:
            data (dict): Data clock out berisi:
                - shiftId (str): ID shift hari ini
                - geometry (dict): Koordinat lokasi GeoJSON format:
                    - type: "Point"
                    - coordinates: [longitude, latitude]
            employee (dict): Data employee yang clock out berisi:
                - _id (str): ID employee
                - name (str): Nama employee
                - branchId (str): ID branch employee
                
        Returns:
            dict: Dictionary berisi:
                - status (bool): Status operasi
                - message (str): Pesan hasil operasi
                
        Raises:
            Exception: Jika terjadi error saat proses clock out
            
        Example:
            >>> employeeClockOut(
            ...     {
            ...         "shiftId": "SHF_2025-10-31_4866",
            ...         "geometry": {
            ...             "type": "Point",
            ...             "coordinates": [110.3695, -7.7956]
            ...         }
            ...     },
            ...     {"_id": "EMP001", "name": "John", "branchId": "STR001"}
            ... )
            {'status': True, 'message': 'Data updated successfully'}
        """
        try:
            print("=================================== EMPLOYEE CLOCK OUT SERVICE ==================================")
            now = pendulum.now("Asia/Jakarta")
            branchId = employee["branchId"]
            employeeId = employee["_id"]
            geometry = GeometrySchema().load(data["geometry"])
            coordinates = geometry["coordinates"]
            
            shiftParent = self.repo.getDataById(id=data["shiftId"])
            
            employeeShift = None
            endTime = None

            for emp in shiftParent["employees"]:
                if emp["employeeId"] == employeeId:
                    if emp["clockIn"] is None or emp["clockIn"] == "":
                        return {"status": False, "message": "Employee not clocked in"}
                    employeeShift = emp["shift"]
                    print("employeeShift = ", employeeShift)
                    break

            if employeeShift is None:
                return {"status": False, "message": "Employee not found in shift"}
            
            shiftTime = self.shiftsRepo.getAllData()
            for shift in shiftTime:
                if shift["shiftName"] == employeeShift:
                    endTime = pendulum.parse(shift["shiftEndTime"], tz="Asia/Jakarta") 
                    break
            if endTime > now:
                return {"status": False, "message": "Clock out time is not yet"}
                
            cek = self.storeRepo.validateCheckIn(coordinates=coordinates, branchId=branchId)
            if cek is None:
                return {"status": False, "message": "Location is outside the allowed radius"}

            current_time = now.to_time_string()
            
            result = self.repo.updateData(
                query={
                    "_id": data["shiftId"],
                    "employees.employeeId": employeeId
                },
                update={
                    "$set": {
                        "employees.$.clockOut": current_time
                    }
                }
            )
            
            if not result.acknowledged:
                return {"status": False, "message": "Failed to update data"}
            
            self.employeeRepo.updateData(query={"_id" : employeeId }, update={
                "$inc" : {
                    "workDays" : 1
                }
            })
            
            history = HistoryService().createHistory(data={
                "employeeId": employee["_id"],
                "employeeName": employee["name"],
                "description": "Clock out data updated successfully",
                "type": "attendance",
                "createdAt": now
            })
            
            if not history["status"]:
                return {"status": False, "message": "Failed to add history"}

            return {"status": True, "message": "Data updated successfully"}
        except Exception as e:
            raise Exception(f"Failed to clock out: {str(e)}")
        

    def employeeClockIn(self, data, employee):
        """
        Proses clock in karyawan dengan validasi lokasi dan waktu.
        
        Method ini menangani proses clock in karyawan dengan melakukan validasi:
        - Lokasi clock in berada dalam radius maksimal 50 meter dari koordinat store
        - Waktu clock in berada dalam window yang diizinkan (30 menit sebelum - 10 menit setelah shift dimulai)
        - Menentukan status kehadiran (present/late) berdasarkan waktu clock in
        
        Aturan Status:
        - Present: Clock in maksimal 10 menit setelah shift dimulai
        - Late: Clock in lebih dari 10 menit setelah shift dimulai
        - Tidak bisa clock in: Lebih dari 30 menit sebelum shift dimulai
        
        Args:
            data (dict): Data clock in berisi:
                - shiftId (str): ID shift hari ini
                - geometry (dict): Koordinat lokasi GeoJSON format:
                    - type: "Point"
                    - coordinates: [longitude, latitude]
            employee (dict): Data employee yang clock in berisi:
                - _id (str): ID employee
                - name (str): Nama employee
                - branchId (str): ID branch employee
                
        Returns:
            dict: Dictionary berisi:
                - status (bool): Status operasi
                - message (str): Pesan hasil operasi (termasuk status present/late)
                
        Raises:
            ValidationError: Jika data tidak valid menurut schema
            Exception: Jika terjadi error saat proses clock in
            
        Example:
            >>> employeeClockIn(
            ...     {
            ...         "shiftId": "SHF_2025-10-31_4866",
            ...         "geometry": {
            ...             "type": "Point",
            ...             "coordinates": [110.3695, -7.7956]
            ...         }
            ...     },
            ...     {"_id": "EMP001", "name": "John", "branchId": "STR001"}
            ... )
            {'status': True, 'message': 'Clocked in successfully as present'}
        """
        try:
            print("=================================== EMPLOYEE CLOCK IN SERVICE ==================================")
            print("data = ", data)
            employeeId = employee["_id"]
            branchId = employee["branchId"]
            geometry = GeometrySchema().load(data["geometry"])
            coordinates = geometry["coordinates"]

            cek = self.storeRepo.validateCheckIn(coordinates=coordinates, branchId=branchId)
            if cek is None:
                return {"status": False, "message": "Location is outside the allowed radius"}
            
            shiftParent = self.repo.getDataById(id=data["shiftId"])
            shiftTime = self.shiftsRepo.getAllData()

            employeeShift = None
            startTime = None

            for emp in shiftParent["employees"]:
                if emp["employeeId"] == employeeId:
                    employeeShift = emp["shift"]
                    print("employeeShift = ", employeeShift)
                    break

            if employeeShift is None:
                return {"status": False, "message": "Employee not found in shift"}

            for shift in shiftTime:
                if shift["shiftName"] == employeeShift:
                    startTime = shift["shiftStartTime"]
                    break

            if startTime is None:
                return {"status": False, "message": "Shift time not found"}

            print("startTime = ", startTime)

            now = pendulum.now("Asia/Jakarta")
            print("now = ", now)
            current_time = now.to_time_string()    

            shift_start = pendulum.from_format(startTime, "HH:mm:ss", tz="Asia/Jakarta")
            late_limit = shift_start.add(minutes=10)
            early_limit = shift_start.subtract(minutes=30)

            print("early_limit = ", early_limit)
            print("now.time() = ", now.time())
            print("early_limit.time() = ", early_limit.time())

            if now.time() < early_limit.time():
                print("now.time() < early_limit.time()")
                return {"status": False, "message": "Employee clock in time is outside the shift time"}

            if now.time() > late_limit.time():
                status = "late"
            else:
                status = "present"

            payload = {
                "employeeId": employeeId,
                "clockIn": current_time,
                "clockOut": None,
                "status": status
            }
            validated = self.EmploAttendSchema.load(payload)
            print("[validated] = ", validated)

            result = self.repo.updateData(
                query={
                    "_id": data["shiftId"],
                    "employees.employeeId": employeeId
                },
                update={ 
                    "$set": {
                        "employees.$.clockIn": validated["clockIn"],
                        "employees.$.status": validated["status"]
                    }
                }
            )

            print(f"[RESULT UPDATE STATUS TO {status.upper()}] = ", result)

            if not result.acknowledged:
                return {"status": False, "message": "Failed to clock in"}
            
            history = HistoryService().createHistory(data={
                "employeeId": employeeId,
                "employeeName": employee["name"],
                "description": f"Clocked in successfully as {status}",
                "type": "attendance",
                "createdAt": now
            })
            
            if not history["status"]:
                return {"status": False, "message": "Failed to add history"}
            
            return {"status": True, "message": f"Clocked in successfully as {status}"}
                
        except ValidationError as e:
            raise ValidationError(e)
        except Exception as e:
            raise Exception(f"Failed to clock in: {str(e)}")
            
    def setShift(self, data, currentUser):
        """
        Menyimpan jadwal shift karyawan untuk satu hari tertentu.
        
        Method ini membuat dokumen shift baru yang berisi daftar karyawan
        dengan shift masing-masing (Day/Night). Setiap tanggal dan branch
        hanya boleh memiliki satu dokumen shift.
        
        Validasi yang dilakukan:
        - Memastikan belum ada shift untuk tanggal dan branch yang sama
        - Memvalidasi shift name (harus ada dalam master shift)
        - Memvalidasi struktur data sesuai schema
        
        Args:
            data (dict): Data shift berisi:
                - Date (str): Tanggal shift format "YYYY-MM-DD"
                - branchId (str): ID branch/store
                - employees (list): List karyawan dengan format:
                    [
                        {
                            "employeeId": "EMP001",
                            "shift": "Day",
                            "clockIn": null,
                            "clockOut": null,
                            "status": "absent"
                        }
                    ]
            currentUser (dict): Data user yang membuat shift berisi:
                - _id (str): ID user
                - name (str): Nama user
                
        Returns:
            dict: Dictionary berisi:
                - status (bool): Status operasi
                - message (str): Pesan hasil operasi
                
        Raises:
            ValidationError: Jika data tidak sesuai dengan schema
            Exception: Jika terjadi error atau shift sudah ada untuk tanggal tersebut
            
        Example:
            >>> setShift(
            ...     {
            ...         "Date": "2025-10-30",
            ...         "branchId": "STR_9820251023235635",
            ...         "employees": [
            ...             {"employeeId": "EMP001", "shift": "Day", "clockIn": null, "clockOut": null},
            ...             {"employeeId": "EMP002", "shift": "Night", "clockIn": null, "clockOut": null}
            ...         ]
            ...     },
            ...     {"_id": "MGR001", "name": "Manager"}
            ... )
            {'status': True, 'message': 'Shift data inserted successfully'}
        """
        try:
            shift_id = f"SHF_{pendulum.now().to_date_string()}_{str(random.randint(1000, 9999))}"
            data["_id"] = shift_id
            date = pendulum.parse(data["Date"], tz="UTC")
            print("-----------DATA ----------: ", date)
            existingShift = self.repo.getData(query={"Date": date, "branchId": data["branchId"]})
            print("=====EXISTING SHIFT: ", existingShift)
            if existingShift:
                return {"status": False, "message": "Shift already exists for this date"}
            valid_shifts = [s["shiftName"] for s in self.shiftsRepo.getAllData()]
            print("VALID SHIFTS:", valid_shifts)

            validated_employees = []
            for emp in data.get("employees", []):
                if emp["shift"] not in valid_shifts:
                    raise Exception(f"Invalid shift name: {emp['shift']}")
                validated_employees.append(self.EmploAttendSchema.load(emp))

            data["employees"] = validated_employees

            validated_data = self.shiftListSchema.load(data)
            result = self.repo.insertData(validated_data)

            if not result.acknowledged:
                return {"status": False, "message": "Failed to insert shift data"}

            history = HistoryService().createHistory(data={
                "employeeId": currentUser["_id"],
                "employeeName": currentUser["name"],
                "description": f"Shift data inserted successfully",
                "type": "shift"
            })
            if not history["status"]:
                raise Exception("Failed to add history")

            
            return {"status": True, "message": "Shift data inserted successfully"}

        except ValidationError as e:
            raise ValidationError(e)
        except Exception as e:
            raise Exception(f"Failed to insert shift data: {str(e)}")
    
    
    # def changeShift(self, data,employee):
    #     try:
    #         print("[UPDATE SHIFT DATA IN SERVICE]:", data)
    #         result = self.repo.updateData(
    #                 query={"_id": data["idShift"], "employees.employeeId": data["employeeId"]},
    #                 update={
    #                     "$set": {
    #                         "employees.$.shift": data["newShift"],
    #                     }
    #                 }
    #             )
    #         print("UPDATE SHIFT RESULT: ", result)
    #         if not result.acknowledged:
    #             return {"status": False, "message": "Failed to update shift data"}

    #         history = HistoryService().createHistory(data={
    #             "employeeId": employee["_id"],
    #             "employeeName": employee["name"],
    #             "description": f"Shift data updated successfully",
    #             "type": "shift"
    #         })  
    #         if not history["status"]:
    #             return {"status": False, "message": "Failed to add history"}                                             
            
    #         return {"status": True, "message": "Shift data updated successfully"}
    #     except ValidationError as e:
    #         raise ValidationError(e)
    #     except Exception as e:
    #         raise Exception(f"Failed to update shift data: {str(e)}")
        
    def removeShift(self,data,id, employee ):
        """
        Menghapus karyawan dari jadwal shift tertentu.
        
        Method ini menghapus satu karyawan dari daftar employees dalam dokumen shift.
        Digunakan ketika karyawan dibatalkan dari jadwal atau ada perubahan jadwal.
        
        Args:
            data (dict): Data yang berisi:
                - employeeId (str): ID karyawan yang akan dihapus dari shift
            id (str): ID dokumen shift
            employee (dict): Data employee yang melakukan penghapusan berisi:
                - _id (str): ID employee
                - name (str): Nama employee
                
        Returns:
            dict: Dictionary berisi:
                - status (bool): Status operasi
                - message (str): Pesan hasil operasi
                
        Raises:
            ValidationError: Jika data tidak valid
            Exception: Jika terjadi error saat remove data
            
        Example:
            >>> removeShift(
            ...     {"employeeId": "EMP001"},
            ...     "SHF_2025-10-31_4866",
            ...     {"_id": "MGR001", "name": "Manager"}
            ... )
            {'status': True, 'message': 'Shift data removed successfully'}
        """
        try:
            print(" =========[REMOVE SHIFT DATA IN SERVICE]: ===========", id)
            
            result = self.repo.updateData(query={"_id": id}, update={
                    "$pull": {
                        "employees": {
                            "employeeId": data["employeeId"]
                        }
                    }
                })
            
            if not result.acknowledged:
                return {"status": False, "message": "Failed to remove shift data"}
            
            history = HistoryService().createHistory({
                "employeeId": employee["_id"],
                "employeeName" : employee["name"],
                "description": f"Shift data removed successfully",
                "type": "shift"
            })
            
            if not history["status"]:
                return {"status": False, "message": "Failed to add history"}
            return {"status": True, "message": "Shift data removed successfully"}

        except ValidationError as e:
            raise ValidationError(e)
        except Exception as e:
            raise Exception(f"Failed to remove shift data: {str(e)}")   
        
    def updateShift(self, data, id, employee ):
        """
        Mengupdate jadwal shift dengan daftar karyawan baru.
        
        Method ini melakukan update lengkap pada dokumen shift, mengganti
        seluruh daftar employees dengan data baru. Berguna untuk melakukan
        perubahan besar pada jadwal seperti menambah/mengurangi banyak karyawan
        atau mengubah shift mereka.
        
        Args:
            data (dict): Data update shift berisi:
                - employees (list): List karyawan baru dengan format:
                    [
                        {
                            "employeeId": "EMP001",
                            "shift": "Day",
                            "clockIn": null,
                            "clockOut": null,
                            "status": "absent"
                        }
                    ]
            id (str): ID dokumen shift yang akan diupdate
            employee (dict): Data employee yang melakukan update berisi:
                - _id (str): ID employee
                - name (str): Nama employee
                
        Returns:
            dict: Dictionary berisi:
                - status (bool): Status operasi
                - message (str): Pesan hasil operasi
                
        Raises:
            ValidationError: Jika data tidak sesuai dengan schema
            Exception: Jika terjadi error atau shift name tidak valid
            
        Example:
            >>> updateShift(
            ...     {
            ...         "employees": [
            ...             {"employeeId": "EMP001", "shift": "Day", "clockIn": null, "clockOut": null},
            ...             {"employeeId": "EMP003", "shift": "Night", "clockIn": null, "clockOut": null}
            ...         ]
            ...     },
            ...     "SHF_2025-10-31_4866",
            ...     {"_id": "MGR001", "name": "Manager"}
            ... )
            {'status': True, 'message': 'Shift data updated successfully'}
        """
        try:
            valid_shifts = [s["shiftName"] for s in self.shiftsRepo.getAllData()]
            print("VALID SHIFTS:", valid_shifts)

            validated_employees = []
            for emp in data.get("employees", []):
                if emp["shift"] not in valid_shifts:
                    raise Exception(f"Invalid shift name: {emp['shift']}")
                validated_employees.append(self.EmploAttendSchema.load(emp))

            data["employees"] = validated_employees

            validated_data = self.updateShiftSchema.load(data)
            result = self.repo.updateData(id=id, validateData=validated_data)
            if not result.acknowledged:
                return {"status": False, "message": "Failed to update shift data"}

            history = HistoryService().createHistory(data={
                "employeeId": employee["_id"],
                "employeeName": employee["name"],
                "description": f"Shift data updated successfully",
                "type": "shift"
            })
            if not history["status"]:
                return {"status": False, "message": "Failed to add history"}
            return {"status": True, "message": "Shift data updated successfully"}
        except ValidationError as e:
            raise ValidationError(e)
        except Exception as e:
            raise Exception(f"Failed to update shift data: {str(e)}")
    
    def getMonthlyShifts(self, branchId, month=None, year=None):
        """
        Mengambil semua jadwal shift dalam satu bulan untuk branch tertentu.
        
        Method ini mengembalikan daftar lengkap jadwal shift beserta detail
        karyawan yang dijadwalkan selama satu bulan. Data diurutkan berdasarkan
        tanggal dari yang paling awal.
        
        Args:
            branchId (str): ID branch/store yang akan diambil jadwalnya
            month (int, optional): Bulan (1-12). Jika None, menggunakan bulan saat ini.
            year (int, optional): Tahun (contoh: 2025). Jika None, menggunakan tahun saat ini.
            
        Returns:
            dict: Dictionary berisi:
                - status (bool): Status operasi
                - message (str): Pesan hasil operasi
                - data (list): List dokumen shift yang sudah diurutkan, setiap shift berisi:
                    - _id: ID shift
                    - Date: Tanggal shift
                    - branchId: ID branch
                    - employees: List karyawan dengan data lengkap
                    
        Raises:
            Exception: Jika terjadi error saat mengambil data
            
        Example:
            getMonthlyShifts("STR_9820251023235635", month=10, year=2025)
            {
                'status': True,
                'message': 'Monthly shifts fetched successfully',
                'data': [
                    {
                        '_id': 'SHF_2025-10-01_1234',
                        'Date': '2025-10-01',
                        'employees': [...]
                    },
                    {
                        '_id': 'SHF_2025-10-02_5678',
                        'Date': '2025-10-02',
                        'employees': [...]
                    }
                ]
            }
        """
        try:
            now = pendulum.now("UTC")
            year = int(year or now.year)
            month = int(month or now.month)

            start_date = pendulum.datetime(year, month, 1, tz="UTC")
            end_date = start_date.add(months=1)

            shifts = self.repo.getAllData(
                query={
                    "branchId": branchId,
                    "Date": {"$gte": start_date, "$lt": end_date}
                },
            )
            for shift in shifts:
                for emp in shift["employees"]:
                    emp["employee"] = self.employeeRepo.getDataById(id=emp["employeeId"])
                    emp["employee"] = EmployeeSchema().dump(emp["employee"])
            shifts = sorted(shifts, key=lambda s: s.get("Date"))
            print("shifts = ", shifts)
            return {"status": True, "message": "Monthly shifts fetched successfully", "data": shifts}
        except Exception as e:
            raise Exception(f"Failed to get monthly shifts: {str(e)}")
    def getMonthlySummary(self, branchId, month=None, year=None):
        
        """
        Mengambil ringkasan data attendance untuk branch tertentu dalam satu bulan.
        
        Method ini mengembalikan daftar ringkasan data attendance yang terdiri
        dari jumlah karyawan yang hadir dan yang terlambat dalam satu bulan.
        
        Args:
            branchId (str): ID branch/store yang akan diambil data attendancenya
            month (int, optional): Bulan (1-12). Jika None, menggunakan bulan saat ini.
            year (int, optional): Tahun (contoh: 2025). Jika None, menggunakan tahun saat ini.
            
        Returns:
            dict: Dictionary berisi:
                - status (bool): Status operasi
                - message (str): Pesan hasil operasi
                - data (dict): Ringkasan data attendance yang terdiri dari:
                    - presentCount (int): Jumlah karyawan yang hadir
                    - lateCount (int): Jumlah karyawan yang terlambat
        example: 
            >>> getMonthlySummary("STR_9820251023235635", month=10, year=2025)
            {
                status : True,
                message : "Monthly summary for 2025-10 fetched successfully",
                data : {
                    "presentCount": 10,
                    "lateCount": 5
                }
            }
            
        Raises:
            Exception: Jika terjadi error saat mengambil data
        """
        try:
            now = pendulum.now("UTC")
            year = int(year or now.year)
            month = int(month or now.month)

            start_date = pendulum.datetime(year, month, 1, tz="UTC")
            end_date = start_date.add(months=1)
            print("------------------start_date = ", start_date)
            shifts = self.repo.getAllData(
                query={
                    "branchId": branchId,
                    "Date": {"$gte": start_date, "$lt": end_date}
                }
            )
            print("------------------shifts = ", shifts)

            if not shifts or len(shifts) == 0:
                return {
                    "status": True,
                    "message": f"No shift data found for {year}-{month:02d}",
                    "data": {"presentCount": 0, "lateCount": 0}
                }

            presentCount = 0
            lateCount = 0
            print("------------------AMBIL STATUS EMPLOYEE = ", shifts)
            for shift in shifts:
                employees = shift.get("employees", [])
                if not isinstance(employees, list):
                    continue

                for emp in employees:
                    status = emp.get("status", "").lower()
                    if status == "present":
                        presentCount += 1
                    elif status == "late":
                        lateCount += 1

            return {
                "status": True,
                "message": f"Monthly summary for {year}-{month:02d}",
                "data": {
                    "presentCount": presentCount,
                    "lateCount": lateCount,
                },
            }

        except Exception as e:
            raise Exception(f"Failed to get monthly summary: {str(e)}")

    def getEmployeeSchedule(self, employeeId, branchId):
        """
    Mengambil jadwal (schedule) untuk seorang employee pada sebuah branch/toko.

    Args:
        employeeId (str): ID employee yang ingin diambil jadwalnya.
        branchId (str): ID branch/store tempat employee terdaftar.

    Returns:
        dict: Dictionary berisi:
            - status (bool): Status operasi.
            - message (str): Pesan hasil operasi.
            - data (list): List schedule (bisa kosong) dengan elemen dict:
                - _id (str): ID shift/penjadwalan.
                - Date (str): Tanggal shift (format sesuai yang tersimpan di DB).
                - shift (str): Nama shift yang dialokasikan untuk employee.
                - clockIn (str|None): Waktu clock in employee (jika ada).
                - clockOut (str|None): Waktu clock out employee (jika ada).
                - status (str|None): Status kehadiran / status lain yang tersimpan.
                - shiftStartTime (str, optional): Waktu mulai shift (jika lookup di shiftsRepo berhasil).
                - shiftEndTime (str, optional): Waktu selesai shift (jika lookup di shiftsRepo berhasil).

    Behavior / Catatan implementasi:
        - Mengambil data shift dari repository utama menggunakan query:
          {"branchId": branchId, "employees.employeeId": employeeId}
        - Mengambil semua definisi shift/time dari shiftsRepo dan membangun map
          berdasarkan shiftName untuk lookup shiftStartTime/shiftEndTime.
        - Untuk setiap shift yang mengandung employeeId, hanya data employee
          yang relevan (baris yang cocok) yang dimasukkan ke `schedule`.
        - Schedule diurutkan berdasarkan field "Date" sebelum dikembalikan.

    Raises:
        Exception: Jika terjadi error saat pengambilan data dari repository
                   atau error lain selama proses. Pesan exception asli akan
                   disertakan (diforward) untuk keperluan debugging.

    Example:
        >>> getEmployeeSchedule("EMP001", "BR_9820251023")
        {
            "status": True,
            "message": "Employee schedule fetched successfully",
            "data": [
                {
                    "_id": "SHF_2025-11-27_9458"
                    "shift": "Night",
                    "Date": "Thu, 27 Nov 2025 00:00:00 GMT",
                    "clockIn": "20:38:22",
                    "clockOut": null,
                    "shiftEndTime": "23:00:00",
                    "shiftStartTime": "15:00:00",
                    "status": "late",
                },
                {
                    "_id": "SHF_2025-11-27_9458"
                    "shift": "Day",
                    "Date": "Thu, 28 Nov 2025 00:00:00 GMT",
                    "clockIn": null,
                    "clockOut": null,
                    "shiftEndTime": "15:00:00",
                    "shiftStartTime": "08:00:00",
                    "status": "absent",
                }
            ]
        }
    """
        try:
            print("GET EMPLOYEE SCHEDULE = ", employeeId, branchId)
            result = self.repo.getAllData(
                query={
                    "branchId": branchId,
                    "employees.employeeId": employeeId
                },
            )

            shift_times = self.shiftsRepo.getAllData()
            shift_time_map = {s["shiftName"]: s for s in shift_times}

            schedule = []

            print("result = ", result)
            for shift in result:
                for emp in shift["employees"]:
                    if emp["employeeId"] == employeeId:
                        shift_name = emp["shift"]
                        data = {
                            "_id" : shift["_id"],
                            "Date": shift["Date"],   
                            "shift": shift_name,
                            "clockIn": emp.get("clockIn"),
                            "clockOut": emp.get("clockOut"),
                            "status": emp.get("status"),
                        }
                        print("data = ", data)
                        data["shiftStartTime"] = shift_time_map[shift_name]["shiftStartTime"]
                        data["shiftEndTime"] = shift_time_map[shift_name]["shiftEndTime"]

                        schedule.append(data)
                        break

            schedule = sorted(schedule, key=lambda s: s.get("Date"))
            print("schedule = ", schedule)
            return {
                "status": True,
                "message": "Employee schedule fetched successfully",
                "data": schedule
            }

        except Exception as e:
            raise Exception("Failed to get employee schedule:", e)
