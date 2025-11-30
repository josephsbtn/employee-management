from repo.historyRepo import HistoryRepo
from validation.historySchema import HistorySchema
from marshmallow import ValidationError
import pendulum
import random

class HistoryService:
    """
    Service class untuk mengelola operasi terkait history/log aktivitas user.
    
    Class ini menyediakan business logic untuk mencatat dan mengambil riwayat
    aktivitas yang dilakukan oleh employee dalam sistem, seperti login,
    operasi CRUD, dan perubahan data penting lainnya.
    
    Attributes:
        repo (HistoryRepo): Repository untuk akses data history
    
    Notes:
        History digunakan untuk audit trail dan tracking aktivitas user
        dalam sistem untuk keperluan monitoring dan keamanan.
    """
    def __init__(self):
        self.repo = HistoryRepo()
        
    def createHistory(self, data):
        """
        Membuat record history baru untuk aktivitas yang terjadi dalam sistem.
        
        Method ini mencatat setiap aktivitas penting yang dilakukan oleh employee,
        seperti login, CRUD operations, atau perubahan status. ID history akan
        di-generate secara otomatis dengan format HIS + random number + timestamp.
        
        Args:
            data (dict): Data history yang akan dicatat dengan struktur:
                {
                    "employeeId": str (ID employee yang melakukan aktivitas),
                    "employeeName": str (nama employee),
                    "description": str (deskripsi aktivitas yang dilakukan),
                    "type": str (tipe aktivitas: "auth", "employee", "store", dll)
                }
        
        Returns:
            dict: Response object dengan struktur:
                - Berhasil:
                    {
                        "status": True,
                        "message": "Data inserted successfully"
                    }
                - Gagal:
                    {
                        "status": False,
                        "message": "Failed to insert data"
                    }
        
        Raises:
            ValidationError: Jika data tidak sesuai dengan schema validasi
            Exception: Jika terjadi error saat menyimpan data ke database
        
        Notes:
            - ID history di-generate dengan format: HIS[random][timestamp]
            - Random number menggunakan range 10-99
            - Timestamp menggunakan timezone default dari pendulum
            - Setiap aktivitas penting dalam sistem harus tercatat di history
        
        Example:
            >>> service = HistoryService()
            >>> history_data = {
            ...     "employeeId": "EMP_123",
            ...     "employeeName": "John Doe",
            ...     "description": "Login successfully",
            ...     "type": "auth"
            ... }
            >>> result = service.createHistory(history_data)
            >>> print(result["message"])
            'Data inserted successfully'
            
            >>> # Contoh history untuk operasi CRUD
            >>> history_data = {
            ...     "employeeId": "EMP_123",
            ...     "employeeName": "John Doe",
            ...     "description": "New employee Jane Smith data inserted successfully",
            ...     "type": "employee"
            ... }
            >>> result = service.createHistory(history_data)
        """
        try:
            data["_id"]  = "HIS" + str(random.randint(10, 99)) + pendulum.now().to_datetime_string()
            data = HistorySchema().load(data)
            res = self.repo.insertData(validateData=data)
            if not res.acknowledged:
                result = {"status": False, "message": "Failed to insert data"}
                return result
            return {"status": True, "message": "Data inserted successfully"}
        except ValidationError as e:
            raise ValidationError(e)
        except Exception as e:
            raise Exception(f"Failed to insert data {e}")
        
    def getAllHistory(self):
        """
        Mengambil semua data history dari database.
        
        Method ini mengambil seluruh riwayat aktivitas yang tercatat dalam sistem,
        biasanya digunakan oleh admin atau owner untuk monitoring aktivitas
        seluruh employee.
        
        Returns:
            dict: Response object dengan struktur:
                - Berhasil:
                    {
                        "status": True,
                        "message": "Data fetched successfully",
                        "data": list[dict] - List history dengan struktur:
                            [{
                                "_id": str,
                                "employeeId": str,
                                "employeeName": str,
                                "description": str,
                                "type": str,
                                "createdAt": datetime
                            }]
                    }
                - Gagal:
                    {
                        "status": False,
                        "message": "Failed to get data"
                    }
        
        Raises:
            Exception: Jika terjadi error saat mengambil data dari database
        
        Notes:
            - Data history diurutkan berdasarkan waktu (biasanya descending)
            - Berguna untuk audit trail dan monitoring sistem secara keseluruhan
            - Dapat difilter lebih lanjut di layer aplikasi jika diperlukan
        
        Example:
            >>> service = HistoryService()
            >>> result = service.getAllHistory()
            >>> if result["status"]:
            ...     for history in result["data"]:
            ...         print(f"{history['employeeName']}: {history['description']}")
            John Doe: Login successfully
            Jane Smith: New employee created
            John Doe: Employee data updated
        """
        try:
            data = self.repo.getAllData()
            if not data:
                result = {"status": False, "message": "Failed to get data"}
                return result
            print(data)
            return {"status": True, "message": "Data fetched successfully", "data": data}
        except Exception as e:
            raise Exception("Failed to get data {e}")
        
    def getUserHistory(self, userId):
        """
        Mengambil riwayat aktivitas dari employee tertentu.
        
        Method ini mengambil semua history yang terkait dengan satu employee
        berdasarkan employeeId. Berguna untuk melihat track record aktivitas
        individual employee atau untuk keperluan investigasi.
        
        Args:
            userId (str): ID employee yang riwayat aktivitasnya ingin diambil
        
        Returns:
            dict: Response object dengan struktur:
                - Berhasil:
                    {
                        "status": True,
                        "message": "Data fetched successfully",
                        "data": list[dict] - List history user tersebut:
                            [{
                                "_id": str,
                                "employeeId": str,
                                "employeeName": str,
                                "description": str,
                                "type": str,
                                "createdAt": datetime
                            }]
                    }
                - Gagal atau tidak ada data:
                    {
                        "status": False,
                        "message": "Failed to get data"
                    }
        
        Raises:
            Exception: Jika terjadi error saat query database
        
        Notes:
            - Hanya menampilkan history dari employee yang diminta
            - Dapat digunakan untuk profile activity user
            - Berguna untuk tracking individual performance atau troubleshooting
        
        Example:
            >>> service = HistoryService()
            >>> result = service.getUserHistory("EMP_123")
            >>> if result["status"]:
            ...     print(f"Total aktivitas: {len(result['data'])}")
            ...     for history in result["data"]:
            ...         print(f"{history['createdAt']}: {history['description']}")
            Total aktivitas: 15
            2025-11-29 10:30:00: Login successfully
            2025-11-29 10:35:00: Updated employee data
            2025-11-29 11:00:00: Created new store
            
            >>> # Contoh ketika user tidak memiliki history
            >>> result = service.getUserHistory("EMP_999")
            >>> print(result["status"])
            False
        """
        try:
            print("---------UDAH DI SERVCIE HISTORY USER---------")
            data = self.repo.getAllData(query={"employeeId": userId})
            print("DATA HISTORY USER",data)
            if not data:
                result = {"status": False, "message": "Failed to get data"}
                return result
            return {"status": True, "message": "Data fetched successfully", "data": data}
        except Exception as e:
            raise Exception("Failed to get data", e)