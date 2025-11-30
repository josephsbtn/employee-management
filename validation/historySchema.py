from marshmallow import Schema, fields, validate
import pendulum

class HistorySchema(Schema):
    """
    Schema untuk memvalidasi dan menserialisasi objek History/Log aktivitas.
    
    Schema ini digunakan untuk memastikan data log yang masuk atau keluar dari sistem 
    memiliki struktur yang benar dan field yang diperlukan.

    Fields:
        _id (str): ID unik dari entri log. Wajib diisi (required).
        employeeId (str): ID unik karyawan yang terkait dengan aktivitas log. Wajib diisi.
        employeeName (str): Nama karyawan yang terkait dengan aktivitas log. Wajib diisi.
        type (str): Tipe atau kategori aktivitas log. Wajib diisi dan harus salah satu 
                    dari nilai yang diperbolehkan (validate.OneOf).
        description (str): Deskripsi detail dari aktivitas yang terjadi. Wajib diisi.
        createdAt (DateTime): Timestamp (waktu dan tanggal) kapan log dibuat. 
                              Hanya digunakan saat memuat (load_only) data dan akan 
                              menggunakan waktu saat ini di zona Jakarta secara default.
    """
    class Meta:
        unknown = "EXCLUDE" # buang fields yang ga sesuai schema
    
    _id = fields.Str(required=True)
    employeeId = fields.Str(required=True)
    employeeName = fields.Str(required=True)
    type = fields.Str(required=True, validate=validate.OneOf(["auth", "branch", "employee", "shift", "attendance", "leave"]))
    description = fields.Str(required=True)
    createdAt = fields.DateTime(load_only=True, load_default=lambda: pendulum.now(tz="Asia/Jakarta"))