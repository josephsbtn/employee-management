from marshmallow import ValidationError
from werkzeug.utils import secure_filename

class FileValidation:
    """
    Kelas untuk menangani logika validasi file, termasuk pemeriksaan ekstensi,
    keamanan nama file, dan batasan ukuran file.

    Attributes:
        whitelistFile (set): Kumpulan ekstensi file yang diperbolehkan.
        MAXSIZE (int): Batas maksimum ukuran file dalam bytes (default 5MB).
    """
    whitelistFile = {"jpg", "png", "jpeg", "pdf"}
    MAXSIZE = 5 * 1024 * 1024 #max 5 mb (1024 = 1 kb) (1024 * 1024 = 1 mb)
    
    def __init__(self, file):
        self.file = file
    
    def validation(self):
        """
        Memvalidasi nama, ekstensi, dan ukuran file yang diunggah.

        Metode ini melakukan langkah-langkah berikut:
        1. Mengamankan nama file menggunakan `secure_filename`.
        2. Memastikan nama file tidak kosong setelah diamankan.
        3. Mengambil ekstensi file dan mencocokkannya dengan `whitelist`.
        4. Menghitung ukuran file dengan memindahkan pointer (kursor).
        5. Memastikan ukuran file tidak melebihi batas `MAXSIZE`.

        ---------------------------------------------------------
        Catatan Keamanan (Werkzeug secure_filename):
        Fungsi `secure_filename` pada langkah 1 sangat krusial untuk:
        * Mencegah serangan Directory Traversal (misal: input `../../hack.sh` 
          akan diubah menjadi `.._.._hack.sh`) agar hacker tidak bisa 
          mengakses atau menimpa file sistem.
        * Mengubah spasi menjadi underscore (_) untuk kompatibilitas OS.
        * Menghapus karakter non-ASCII yang berpotensi error di server.
        ---------------------------------------------------------

        Returns:
            dict: Dictionary yang berisi detail file yang valid:
                - 'fileType' (str): Ekstensi file (contoh: 'jpg').
                - 'fileName' (str): Nama file yang sudah diamankan.

        Raises:
            ValidationError: Jika nama file kosong, tipe file tidak diizinkan,
                           atau ukuran file melebihi batas maksimum.
            Exception: Jika terjadi kesalahan tak terduga selama proses validasi.
        """
        try:
            filename = secure_filename(self.file.filename)
            if filename == "":
                raise ValidationError("File name cannot be empty")
            
            fileType = filename.split(".",1)[-1].lower()
            if fileType not in self.whitelistFile:
                raise ValidationError("Invalid file type")
            
            self.file.seek(0, 2) #gerakin pointer dari awal file sampe akhir buat ngukur size file nya
            fileSize = self.file.tell() #.tell tu ngasih tau posisi terakhir pointer nya jadi tau size nya berapa dari posisi terakhir pointer
            self.file.seek(0) #pointer di balikin lagi ke titik awal file biar waktu di upload, file tidak corrupt
            if fileSize > self.MAXSIZE:
                raise ValidationError("File size is too large")
            return {"fileType": fileType, "fileName": filename}
            
        except ValidationError as e:
            raise ValidationError(e)
        except Exception as e:
            raise Exception(f"Failed to validate file {e}")