from marshmallow import Schema, fields, validate, pre_load
import pendulum
from validation.storeSchema import GeometrySchema
    

class EmployeeAttendanceSchema(Schema): #FIX
    """
    Schema untuk validasi data kehadiran karyawan pada shift tertentu.
    
    Schema nested yang digunakan dalam ShiftListSchema untuk menyimpan
    informasi clock-in/clock-out setiap karyawan dalam satu shift kerja.
    Mendukung multiple status kehadiran (late, present, absent).
    
    Validasi Fields:
        employeeId (str):
            - Required, ID karyawan yang mengisi absensi
            - Foreign key ke collection employees
            
        shift (str):
            - Optional, nama shift yang diambil karyawan
            - Contoh: "Morning Shift", "Night Shift", "Shift A"
            
        clockIn (str):
            - Optional, waktu clock-in karyawan
            - Format: "HH:MM:SS" (ISO time string)
            - Allow None untuk karyawan yang absent
            - Auto-parse dari string ISO datetime ke time string
            
        clockOut (str):
            - Optional, waktu clock-out karyawan
            - Format: "HH:MM:SS" (ISO time string)
            - Allow None untuk karyawan yang belum clock-out atau absent
            - Auto-parse dari string ISO datetime ke time string
            
        status (str):
            - Default: "absent"
            - Values: "late" (terlambat), "present" (hadir tepat waktu), "absent" (tidak hadir)
            - Determined by comparison clockIn vs shift.clockIn
    
    Fitur Auto-Parse:
        - String ISO datetime otomatis diparse ke time string (HH:MM:SS)
        - Contoh: "2025-01-15T08:30:00+07:00" -> "08:30:00"
        - Timezone: Asia/Jakarta
    
    Status Logic:
        - "absent": clockIn = None (tidak clock-in sama sekali)
        - "present": clockIn <= shift.clockIn + tolerance (tepat waktu)
        - "late": clockIn > shift.clockIn + tolerance (terlambat)
    
    Usage Example:
       # Nested dalam ShiftListSchema
       attendance_data = {
           "employeeId": "emp_001",
           "shift": "Morning Shift",
           "clockIn": "2025-01-15T08:00:00+07:00",
           "clockOut": "2025-01-15T17:00:00+07:00",
           "status": "present"
       }
       schema = EmployeeAttendanceSchema()
       result = schema.load(attendance_data)
       # clockIn: "08:00:00", clockOut: "17:00:00"
        
       # Karyawan terlambat
         late_data = {
             "employeeId": "emp_002",
             "shift": "Morning Shift",
             "clockIn": "2025-01-15T08:45:00+07:00",
             "status": "late"
         }
         result = schema.load(late_data)
        
        # Karyawan absent
        absent_data = {
            "employeeId": "emp_003",
            "shift": "Morning Shift",
            "clockIn": None,
            "clockOut": None,
            "status": "absent"
        }
        result = schema.load(absent_data)
    
    Notes:
        - clockIn dan clockOut allow None untuk flexibility
        - Status ditentukan oleh business logic di service layer
        - Time string format untuk kemudahan perbandingan waktu
        - Digunakan dalam array employees di ShiftListSchema
    """
    @pre_load
    def sanitized(self, data, **kwargs):
        timeField = ["clockIn", "clockOut"]
        
        for field in timeField:
            if field in data and isinstance(data.get(field), str):
                data[field] = pendulum.parse(data[field], tz="Asia/Jakarta").to_time_string()
        return data
        
    employeeId = fields.Str(required=True)
    shift = fields.Str(required=False)
    clockIn = fields.Str(allow_none=True)
    clockOut = fields.Str(allow_none=True)
    status = fields.Str(
        validate=validate.OneOf(["late", "present", "absent"]),
        load_default="absent"
    )

class ShiftListSchema(Schema):
    """
    Schema untuk validasi shift kerja harian dan daftar kehadiran karyawan.
    
    Schema utama untuk manajemen shift dan attendance tracking. Menyimpan
    informasi shift per tanggal per branch beserta array kehadiran semua
    karyawan yang dijadwalkan pada shift tersebut.
    
    Validasi Fields:
        _id (str):
            - Required, unique identifier untuk shift list
            - Format: "shift_[branchId]_[YYYYMMDD]"
            - Contoh: "shift_branch001_20250115"
            
        Date (datetime):
            - Required, tanggal shift ini berlaku
            - Format: ISO 8601 datetime
            - Digunakan untuk filtering dan reporting
            
        branchId (str):
            - Required, ID cabang tempat shift ini berlaku
            - Foreign key ke collection branches
            - Setiap branch bisa punya shift schedule berbeda
            
        employees (list):
            - Array of EmployeeAttendanceSchema objects
            - List semua karyawan yang dijadwalkan shift hari ini
            - Includes: employeeId, shift, clockIn, clockOut, status
            
        createdAt (datetime):
            - Auto-generated, timestamp pembuatan shift list
            - Timezone: Asia/Jakarta
            - Digunakan untuk audit trail
    
    Data Structure:
        {
            "_id": "shift_branch001_20250115",
            "Date": "2025-01-15T00:00:00+07:00",
            "branchId": "branch_001",
            "employees": [
                {
                    "employeeId": "emp_001",
                    "shift": "Morning Shift",
                    "clockIn": "08:00:00",
                    "clockOut": "17:00:00",
                    "status": "present"
                },
                {
                    "employeeId": "emp_002",
                    "shift": "Morning Shift",
                    "clockIn": "08:45:00",
                    "clockOut": None,
                    "status": "late"
                }
            ],
            "createdAt": "2025-01-15T00:00:00+07:00"
        }
    
    Usage Examples:
        # Create Daily Shift List
        schema = ShiftListSchema()
        shift_data = {
            "_id": "shift_branch001_20250115",
            "Date": "2025-01-15T00:00:00",
            "branchId": "branch_001",
            "employees": [
                {
                    "employeeId": "emp_001",
                    "shift": "Morning Shift",
                    "clockIn": None,
                    "clockOut": None,
                    "status": "absent"
                },
                {
                    "employeeId": "emp_002",
                    "shift": "Morning Shift",
                    "clockIn": None,
                    "clockOut": None,
                    "status": "absent"
                }
            ]
        }
        result = schema.load(shift_data)
        # createdAt: auto-generated
        # Status semua karyawan default "absent" sampai mereka clock-in
        
        # Shift List dengan Mixed Status
        shift_data = {
            "_id": "shift_branch001_20250115",
            "Date": "2025-01-15T00:00:00",
            "branchId": "branch_001",
            "employees": [
                {
                    "employeeId": "emp_001",
                    "shift": "Morning Shift",
                    "clockIn": "08:00:00",
                    "clockOut": "17:00:00",
                    "status": "present"
                },
                {
                    "employeeId": "emp_002",
                    "shift": "Morning Shift",
                    "clockIn": "08:30:00",
                    "clockOut": None,
                    "status": "late"
                },
                {
                    "employeeId": "emp_003",
                    "shift": "Morning Shift",
                    "clockIn": None,
                    "clockOut": None,
                    "status": "absent"
                }
            ]
        }
        result = schema.load(shift_data)
    
    Business Logic:
        1. Shift list dibuat setiap hari untuk setiap branch
        2. Semua karyawan yang scheduled otomatis masuk dengan status "absent"
        3. Saat karyawan clock-in, status berubah ke "present" atau "late"
        4. Clock-out optional (bisa None jika belum clock-out)
        5. Late tolerance ditentukan di shift configuration (e.g., 15 menit)
    
    Reporting Use Cases:
        - Daily attendance report per branch
        - Late employee tracking
        - Payroll calculation (workDays increment) *incoming feature
        - Performance metrics (attendance rate)
    
    Notes:
        - Satu shift list per tanggal per branch
        - _id harus unique (kombinasi branchId + Date)
        - Update attendance menggunakan updateListSchema
        - createdAt untuk audit, tidak boleh diubah
    """
    
    _id = fields.Str(required=True)
    Date = fields.DateTime(required=True)
    branchId = fields.Str(required=True)
    employees = fields.List(fields.Nested(EmployeeAttendanceSchema))
    createdAt = fields.DateTime(load_only=True, load_default=lambda: pendulum.now(tz="Asia/Jakarta"))
   
class updateListSchema(Schema):
    employees = fields.List(fields.Nested(EmployeeAttendanceSchema))
    updatedAt = fields.DateTime(load_only=True, load_default=lambda: pendulum.now(tz="Asia/Jakarta")) 

class shiftSchema(Schema):
    _id = fields.Str(required=True)
    shiftName = fields.Str(required=True)
    clockIn = fields.DateTime(format="%H:%M",required=False)
    clockOut = fields.DateTime(format="%H:%M",required=False)