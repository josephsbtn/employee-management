from marshmallow import Schema, fields, validate, ValidationError, pre_load
import pendulum
from utils.utility import Utility

def validateAventraEmail(value):
    if not value.endswith('@aventra.com'):
        raise ValidationError('Email must end with @aventra.com')

class EmployeeSchema(Schema):
    """
    Schema untuk validasi dan sanitasi data karyawan.
    
    Load vs Dump:
        - Load: Validasi data masuk (Dict => Python object)
        - Dump: Serialisasi data keluar (Python object => Dict) dengan filtering field
    
    Validasi Fields:
        _id (str): 
            - ID unik karyawan (dump_only, auto-generated oleh database)
            
        name (str): 
            - Required, minimal 2 karakter, maksimal 60 karakter
            - Tidak boleh mengandung angka (0-9) atau karakter spesial (@#$%^&*)
            - Auto-sanitasi: HTML tags dihapus, double space dibersihkan
            
        email (str): 
            - Required, format email valid
            - Harus berakhiran @aventra.com (domain perusahaan)
            - Auto-sanitasi: lowercase, trim whitespace, hapus HTML
            
        role (str): 
            - Required, hanya menerima: "owner", "manager", atau "employee"
            - Menentukan level akses dalam sistem
            
        password (str): 
            - Required untuk create, optional untuk update
            - Minimal 8 karakter
            - load_only: tidak akan di-dump ke response (keamanan)
            
        salaryPerDay (float): 
            - Optional, range: Rp 10.000 - Rp 100.000
            - Gaji harian karyawan
            
        annualLeaveBalance (int):
            - Default: 13 hari
            - Range: 0-13 hari
            - Jatah cuti tahunan karyawan
            
        workDays (int):
            - Default: 0
            - Counter jumlah hari kerja karyawan
            
        branchId (str): 
            - Required, ID cabang tempat karyawan bekerja
            - Foreign key ke collection branches
            
        status (str): 
            - Default: "active"
            - Values: "active" atau "inactive"
            - Status keaktifan karyawan
            
        createdAt (datetime): 
            - dump_only, auto-generated
            - Timestamp pembuatan data (timezone: Asia/Jakarta)
    
    Fitur Sanitasi Otomatis:
        1. HTML Injection Prevention: Menghapus semua HTML tags dari name & email
        2. Whitespace Normalization: Menghapus double/multiple spaces
        3. Email Standardization: Konversi ke lowercase dan trim
        4. Unknown Fields: Otomatis dibuang (EXCLUDE)
    
    Usage Examples:
        # Create Employee
        schema = CreatedEmployeeSchema()
        data = {
            "name": "John Doe",
            "email": "john@aventra.com",
            "role": "employee",
            "password": "securepass123",
            "salaryPerDay": 50000,
            "branchId": "branch_001"
        }
        result = schema.load(data)
        # result siap disimpan ke database
        
        # Update Employee
        schema = UpdateEmployeeSchema()
        data = {"name": "John Smith", "salaryPerDay": 55000}
        result = schema.load(data)
    
        # Serialize Employee (dump)
        employee = db.employees.find_one({"_id": "emp_001"})
        schema = EmployeeSchema()
        result = schema.dump(employee)
        # password tidak akan muncul di result
    
    Validation Error Examples:
        schema.load({"name": "J", "email": "invalid"})
        ValidationError({
            'name': ['Shorter than minimum length 2.'],
            'email': ['Not a valid email address.'],
            'role': ['Missing data for required field.'],
            'branchId': ['Branch ID is required.']
        })
        
        schema.load({"name": "John123", "email": "john@gmail.com"})
        ValidationError({
            'name': ['Name cannot contain special characters.'],
            'email': ['Email must end with @aventra.com']
        })
    
    Notes:
        - Gunakan CreatedEmployeeSchema untuk operasi create (auto-set createdAt)
        - Gunakan UpdateEmployeeSchema untuk operasi update (auto-set updateAt)
        - Password selalu load_only untuk keamanan
        - Field unknown akan otomatis dibuang (Meta.unknown = "EXCLUDE")
    """
    utility = Utility()
    
    class Meta:
        unknown = "EXCLUDE" # buang fields yang ga sesuai schema
    
    @pre_load
    def sanitize(self, data, **kwargs):
        """
        Sanitasi data sebelum validasi untuk mencegah XSS dan normalisasi format.
        
        Proses sanitasi:
            1. Hapus HTML tags dari name dan email
            2. Hapus double/multiple spaces
            3. Convert email ke lowercase
            4. Trim whitespace di awal/akhir
        
        Args:
            data (dict): Data input yang akan disanitasi
            **kwargs: Parameter tambahan dari marshmallow (many, partial, unknown)
        
        Returns:
            dict: Data yang sudah disanitasi dan siap divalidasi
            
        Example:
            data = {"name": "John  <script>alert('xss')</script>  Doe", 
                    "email": "  JOHN@AVENTRA.COM  "}
            sanitized = self.sanitize(data)
            # Result: {"name": "John Doe", "email": "john@aventra.com"}
        """
        sanitizeFields = ['name', 'email']
        
        for field in sanitizeFields:
            # Cek apakah field ada dan memiliki nilai yang valid
            if field in data and data.get(field):
                self.utility.blockMongoInject(data[field])
                data[field] = self.utility.sanitizeHTML(data[field])
                data[field] = self.utility.deleteDoubleSpace(data[field])
        
        # Lowercase email jika ada dan valid
        if data.get('email') and isinstance(data['email'], str):
            data['email'] = data['email'].lower().strip()
        
        return data
        
    _id = fields.Str(required=False, dump_only=True)
    name = fields.Str(
        required=True,
        validate=[validate.Length(min=2, max=60), validate.NoneOf(['@', '#', '$', '%', '^', '&', '*', "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"])],
        error_messages={"required": "Name is required.",
                        "invalid": "Name cannot contain special characters."}
    )

    email = fields.Email(
        required=True,
        validate= [validateAventraEmail, validate.Length(min=2, max=60)],
        error_messages={
            "required": "Email is required.",
            "invalid": "Email must end with @aventra.com"
        }
    )

    role = fields.Str(
        required=True,
        validate=validate.OneOf(["owner", "manager", "employee"]),
        error_messages={"required": "Role is required."},
    )

    password = fields.Str(
        required=False,
        validate=validate.Length(min=8),
        load_only=True, 
        error_messages={"required": "Password is required."}
    )

    salaryPerDay = fields.Float(
        required=False,
        validate=validate.Range(min=10000, max=100000),
        error_messages={"required": "Salary is required."}
    )
    
    annualLeaveBalance = fields.Int(load_default=13, validate=validate.Range(min=0, max=13))
    workDays = fields.Int(load_default=0)
    lateDays = fields.Int(load_default=0)
    branchId = fields.Str(
        required=True,
        error_messages={"required": "Branch ID is required."}
    )

    status = fields.Str(
        validate=validate.OneOf(["active", "inactive"]),
        load_default="active"
    )
    createdAt = fields.DateTime(dump_only=True)
        
class LoginSchema(Schema):
    utility = Utility()
    
    @pre_load
    def sanitize(self, data, **kwargs):
        if data.get('email') and isinstance(data['email'], str):
            data['email'] = data['email'].lower().strip()
            self.utility.blockMongoInject(data)     
        return data
    
    email = fields.Email(
        required=True,
        validate=validate.Length(min=2, max=60),
        error_messages={"required": "Email is required."}
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        error_messages={"required": "Password is required."}
    )
    
class UpdateEmployeeSchema(EmployeeSchema):
    updateAt = fields.DateTime( load_default=lambda: pendulum.now(tz="Asia/Jakarta"))


class CreatedEmployeeSchema(EmployeeSchema):
    createdAt = fields.DateTime(load_default=lambda: pendulum.now(tz="Asia/Jakarta"))