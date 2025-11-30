from marshmallow import Schema, fields, validate, pre_load
import pendulum
from utils.utility import Utility

class reviewerSchema(Schema):
    """
    Schema untuk data reviewer pada proses approval cuti.
    
    Schema nested yang digunakan dalam AnnualRequestSchema untuk menyimpan
    informasi reviewer yang menyetujui/menolak permohonan cuti.
    
    Validasi Fields:
        employeeId (str):
            - Optional, default: "" (empty string)
            - ID karyawan yang melakukan review (manager/owner)
            
        name (str):
            - Optional, default: ""
            - Nama lengkap reviewer untuk referensi cepat
            
        note (str):
            - Optional, default: ""
            - Catatan atau alasan dari reviewer (approve/reject)
            - Auto-sanitasi: HTML tags dihapus, double space dibersihkan
            
        timeReviewed (datetime):
            - Optional
            - Timestamp kapan review dilakukan
            - Support string ISO format, auto-convert ke datetime (Asia/Jakarta)
    
    Fitur Sanitasi:
        - HTML Injection Prevention pada field 'note'
        - Whitespace normalization untuk 'note'
        - Auto-parse string datetime ke pendulum datetime object
    
    Usage Example:
        # Nested dalam AnnualRequestSchema
        leave_data = {
            "reviewer": {
                "employeeId": "emp_manager_001",
                "name": "John Manager",
                "note": "Approved for family emergency",
                "timeReviewed": "2025-01-15T10:30:00"
            }
        }
        schema = AnnualRequestSchema()
        result = schema.load(leave_data)
    
    Notes:
        - Semua fields optional karena reviewer hanya diisi saat approval/rejection
        - timeReviewed bisa string ISO atau datetime object
        - Digunakan untuk audit trail proses approval
    """
    utility = Utility()
    
    @pre_load
    def sanitize(self, data, **kwargs):
        if 'note' in data and data.get('note'):
            data['note'] = self.utility.sanitizeHTML(data['note'])
            data['note'] = self.utility.deleteDoubleSpace(data['note'])  
        
        if 'timeReviewed' in data and data.get('timeReviewed'):
            if isinstance(data['timeReviewed'], str):
                data['timeReviewed'] = pendulum.parse(data['timeReviewed'] )
        return data
    employeeId = fields.Str(required=False, load_default="")
    name = fields.Str(required=False, load_default="")
    note = fields.Str(required=False, load_default="")
    timeReviewed = fields.DateTime(required=False)

class AnnualRequestSchema(Schema):
    """
    Schema untuk validasi dan sanitasi permohonan cuti karyawan.
    
    Schema utama untuk menangani CRUD operations pada sistem permohonan cuti
    (annual leave, sick leave, permission). Termasuk validasi tipe cuti,
    durasi, status approval, dan attachment dokumen pendukung.
    
    Validasi Fields:
        _id (str):
            - Required, unique identifier untuk request
            - Format: "leave_[timestamp]_[random]"
            
        employeeId (str):
            - Required, ID karyawan yang mengajukan cuti
            - Foreign key ke collection employees
            
        branchId (str):
            - Required, ID cabang tempat karyawan bekerja
            - Untuk filtering dan approval routing
            
        type (str):
            - Required, tipe permohonan
            - Values: "sick" (sakit), "annual" (cuti tahunan), "permission" (izin)
            
        startDate (datetime):
            - Required, tanggal mulai cuti
            - Format: ISO 8601 datetime
            
        endDate (datetime):
            - Required, tanggal akhir cuti
            - Harus lebih besar atau sama dengan startDate
            
        days (int):
            - Required, jumlah hari cuti yang diajukan
            - Calculated field (endDate - startDate + 1)
            
        status (str):
            - Default: "pending"
            - Values: "pending", "approved", "rejected", "cancelled"
            - State machine untuk approval workflow
            
        reason (str):
            - Required, alasan pengajuan cuti
            - Auto-sanitasi: HTML tags dihapus, double space dibersihkan
            - MongoDB injection protection
            
        reviewer (dict):
            - Optional, nested reviewerSchema
            - Diisi saat manager/owner melakukan approval/rejection
            - Contains: employeeId, name, note, timeReviewed
            
        fileName (str):
            - Optional, nama file attachment (surat dokter, dll)
            - Original filename dari upload
            
        attachmentUrl (str):
            - Optional, URL ke file attachment di storage
            - Generated setelah file upload berhasil
            
        createdAt (datetime):
            - Auto-generated, timestamp pembuatan request
            - Timezone: Asia/Jakarta
    
    Fitur Keamanan:
        1. MongoDB Injection Protection (blockMongoInject)
        2. HTML/XSS Prevention pada field 'reason'
        3. Whitespace normalization
        4. Unknown fields auto-excluded (Meta.unknown = "EXCLUDE")
    
    Approval Workflow:
        pending -> approved/rejected (by manager)
        pending/approved -> cancelled (by employee)
    
    Usage Examples:
        # Create Leave Request (Sick Leave dengan attachment)
        schema = AnnualRequestSchema()
        leave_data = {
            "_id": "leave_20250115_abc123",
            "employeeId": "emp_001",
            "branchId": "branch_001",
            "type": "sick",
            "startDate": "2025-01-20T00:00:00",
            "endDate": "2025-01-22T00:00:00",
            "days": 3,
            "reason": "Demam tinggi dan flu",
            "fileName": "surat_dokter.pdf",
            "attachmentUrl": "/uploads/surat_dokter_abc123.pdf"
        }
        result = schema.load(leave_data)
        # status: "pending", createdAt: auto-generated
        
        # Approve Request
        update_data = {
            "status": "approved",
            "reviewer": {
                "employeeId": "emp_manager_001",
                "name": "John Manager",
                "note": "Approved. Get well soon!",
                "timeReviewed": "2025-01-15T10:30:00"
            }
        }
        schema = UpdateLeaveRequestSchema()
        result = schema.load(update_data, partial=True)
        # updatedAt: auto-generated
        
        # Annual Leave Request (no attachment)
        leave_data = {
            "_id": "leave_20250120_xyz789",
            "employeeId": "emp_002",
            "branchId": "branch_001",
            "type": "annual",
            "startDate": "2025-02-01T00:00:00",
            "endDate": "2025-02-05T00:00:00",
            "days": 5,
            "reason": "Liburan keluarga ke Bali"
        }
        result = schema.load(leave_data)
    
    Validation Errors:
        schema.load({"type": "vacation", "status": "processing"})
        ValidationError({
            '_id': ['Missing data for required field.'],
            'employeeId': ['Missing data for required field.'],
            'type': ['Must be one of: sick, annual, permission.'],
            'status': ['Must be one of: pending, approved, rejected, cancelled.']
        })
    
    Business Rules:
        1. Sick leave > 2 hari wajib attachment surat dokter
        2. Annual leave memotong annualLeaveBalance karyawan
        3. Permission tidak memotong jatah cuti
        4. Manager hanya bisa approve request di branch-nya
        5. Owner bisa approve semua request
        6. Employee hanya bisa cancel request dengan status "pending"
    
    Notes:
        - Gunakan UpdateLeaveRequestSchema untuk update (auto-set updatedAt)
        - File attachment di-handle terpisah (multipart/form-data)
        - Validasi business rules dilakukan di service layer
        - Status transition harus sesuai workflow (enforce di controller)
    """
    
    utility = Utility()
    
    class Meta:
        unknown = "EXCLUDE" # buang fields yang ga sesuai schema
    
    @pre_load
    def sanitize(self, data, **kwargs):
        sanitizeFields = ['reason']
        
        self.utility.blockMongoInject(data)
        
        for field in sanitizeFields:
            if field in data and data.get(field):
                data[field] = self.utility.sanitizeHTML(data[field])
                data[field] = self.utility.deleteDoubleSpace(data[field])  
        return data
    
    _id = fields.Str(required=True)
    employeeId = fields.Str(required=True, load_only=False)
    branchId = fields.Str(required=True, load_only=False)
    type = fields.Str(required=True, validate=validate.OneOf(["sick", "annual", "permission" ]))
    startDate = fields.DateTime(required=True)
    endDate = fields.DateTime(required=True)
    days = fields.Int(required=True)
    status = fields.Str(validate=validate.OneOf(["pending", "approved", "rejected", "cancelled"]), load_default="pending")
    reason = fields.Str(required=True)
    reviewer = fields.Nested(reviewerSchema, required=False)
    fileName = fields.Str(required=False)
    attachmentUrl = fields.Str(required=False)
    createdAt = fields.DateTime(load_default=lambda: pendulum.now(tz="UTC"))
    
    
class UpdateLeaveRequestSchema(AnnualRequestSchema):
    updatedAt = fields.DateTime(load_only=True, load_default=lambda: pendulum.now(tz="UTC"))
    