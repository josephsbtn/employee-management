from marshmallow import Schema, fields, validate, pre_load
import pendulum
from utils.utility import Utility

class GeometrySchema(Schema):
    """
    Schema untuk struktur data lokasi geospasial (GeoJSON Point).
    
    Schema nested yang digunakan dalam StoreSchema untuk menyimpan koordinat
    garis lintang (latitude) dan garis bujur (longitude) toko. Struktur ini
    mengikuti standar GeoJSON yang kompatibel dengan index '2dsphere' di MongoDB.
    
    Validasi Fields:
        type (str):
            - Optional, load_default: "Point"
            - Menentukan tipe geometri GeoJSON
            - Secara default diset ke "Point" untuk lokasi tunggal
            
        coordinates (List[float]):
            - Required
            - Array berisi tepat 2 angka desimal (float)
            - Format urutan: [Longitude, Latitude] atau [Garis Bujur, Garis Lintang]
            - Validasi panjang array harus tepat 2 elemen
    
    Usage Example:
        # JSON input
        {
            "type": "Point",
            "coordinates": [106.827153, -6.175110] 
        }
    
    Notes:
        - Urutan koordinat SANGAT PENTING untuk query MongoDB: [Longitude, Latitude].
        - Jangan terbalik dengan format Google Maps (Lat, Long).
    """
    type = fields.Str(
        load_default="Point"
    )
    coordinates = fields.List(
        fields.Float(),
        required=True,
        validate=validate.Length(equal=2)
    )

class StoreSchema(Schema):
    """
    Schema utama untuk validasi dan sanitasi data Toko (Store).
    
    Schema ini menangani validasi input data toko baru, termasuk pembersihan karakter
    berbahaya (XSS), validasi format nama/alamat, dan struktur lokasi nested.
    
    Validasi Fields:
        _id (str):
            - Required
            - Unique Identifier untuk toko (biasanya string ObjectId dari MongoDB)
            
        name (str):
            - Required
            - Panjang karakter: min 2, max 50
            - Blacklist chars: ['@', '#', '$', '%', '^', '&', '*']
            - Sanitasi aktif: HTML tags stripping & double space removal
            
        address (str):
            - Required
            - Panjang karakter: min 2, max 150
            - Blacklist chars: ['@', '#', '$', '%', '^', '&', '*']
            - Sanitasi aktif: HTML tags stripping & double space removal
            
        status (str):
            - Optional, load_default: "active"
            - Status operasional toko
            - Strict Enum: Hanya menerima "active" atau "inactive"
            
        geometry (Nested):
            - Required
            - Object nested menggunakan GeometrySchema
            - Menyimpan koordinat lokasi toko
            
        createdAt (str):
            - Optional (Auto-generated)
            - Timestamp pembuatan data
            - Format: String ISO 8601
    
    Fitur Sanitasi (@pre_load):
        - HTML Injection Prevention: Menghapus tag HTML pada field 'name' dan 'address'
        - Whitespace Normalization: Mengubah spasi ganda menjadi spasi tunggal
        - Sanitasi dijalankan SEBELUM validasi panjang karakter (Length validator)
    
    Usage Example:
        store_data = {
            "_id": "store_123",
            "name": "   Toko  <b>Makmur</b>   Jaya   ",  # Akan disanitasi jadi "Toko Makmur Jaya"
            "address": "Jl. Sudirman No. 1",
            "geometry": {
                "coordinates": [110.12345, -7.12345]
            }
        }
        schema = StoreSchema()
        result = schema.load(store_data)
        
    Notes:
        - Error custom message disediakan untuk validasi 'required' dan 'invalid chars'.
        - Validasi karakter spesial bertujuan mencegah SQL Injection sederhana atau format nama yang aneh.
    """
    class Meta:
        unknown = "EXCLUDE" 
        
    utility = Utility()
    
    @pre_load
    def sanitize(self, data, **kwargs):
        """
        Hook yang berjalan SEBELUM validasi schema dimulai (Pre-processing).
        
        Tugas:
        1. Membersihkan tag HTML (mencegah XSS sederhana).
        2. Menghapus spasi ganda (double space) menjadi satu spasi.
        
        Args:
            data (dict): Data mentah (raw data) yang dikirim user.
            
        Returns:
            dict: Data yang sudah dibersihkan.
        """
        sanitizeFields = ['name', 'address']
        
        for field in sanitizeFields:
            if field in data and data.get(field):
                data[field] = self.utility.sanitizeHTML(data[field])
                data[field] = self.utility.deleteDoubleSpace(data[field])
        return data
    
    _id = fields.Str(required=True)
    name = fields.Str(required=True, validate=[validate.Length(min=2, max=50), validate.ContainsNoneOf(['@', '#', '$', '%', '^', '&', '*'])],
                      error_messages={"required": "Name is required.", 
                                      "invalid": "Name cannot contain special characters."})
    address = fields.Str(required=True, validate=[validate.Length(min=2, max=150),validate.ContainsNoneOf(['@', '#', '$', '%', '^', '&', '*'])],
                         error_messages={"required": "Address is required.", 
                                         "invalid": "Address cannot contain special characters."})
    status = fields.Str(validate=validate.OneOf(["active", "inactive"]), load_default="active")
    geometry = fields.Nested(
        GeometrySchema,
        required=True,
    )
    createdAt = fields.Str(dump_only=True)

class createStoreSchema(StoreSchema):
    createdAt = fields.Str(required=False, load_default=lambda: pendulum.now(tz="Asia/Jakarta"))
    
    
class UpdateStoreSchema(StoreSchema):
    updatedAt = fields.Str(required=False, load_default=lambda: pendulum.now(tz="Asia/Jakarta"))
