import jwt
from repo.sessionRepo import SessionRepo
from datetime import timedelta, datetime
from utils.config import Config
import pendulum


class SessionService:
    """
    Service untuk mengelola session dan autentikasi pengguna menggunakan JWT (JSON Web Token).
    Menangani proses pembuatan, validasi, dan penghapusan token, serta pengecekan hak akses pengguna.
    """

    def __init__(self):
        """Inisialisasi service dengan repository session untuk koneksi ke database."""
        self.repo = SessionRepo()
        
    def createToken(self, data):
        """
        Membuat token JWT baru dan menyimpannya ke database.

        Args:
            data (dict): Data pengguna yang digunakan untuk membuat token.
                Contoh:
                {
                    "_id": "",
                    "name": "John Doe",
                    "role": "manager",
                    "email": "john@example.com",
                    "password": "hashed_password",
                    "status": "active",
                    "branchId": "652ca8f17c8b83b4567abcd",
                    "salary": 5000000
                }

        Returns:
            str: Token JWT yang berhasil dibuat dan disimpan.

        Raises:
            Exception: Jika token gagal dibuat atau disimpan.

        ---
        ✅ Contoh Output Berhasil:
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

        ❌ Contoh Output Gagal:
        Exception: Failed to create token: Invalid ObjectId format.
        """
        try:
            if data["status"] == "inactive":
                raise Exception("User is inactive")
            now = pendulum.now()

            payload = {
                "name": data["name"],
                "role": data["role"],
                "_id": data["_id"],
                "iat": now,
                "exp": now + pendulum.duration(hours=8),
            }
            
            if payload["role"] != "owner":
                payload["branchId"] = data["branchId"]
                
            token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")

            session = {
                "name": data["name"],
                "role": data["role"],
                "token": token,
                "iat": now,
                "exp": now + pendulum.duration(hours=8),
            }   

            insert = self.repo.insertData(session)
            if not insert:
                raise Exception("Failed to create token")

            return token
        except Exception as e:
            raise Exception(f"Failed to create token: {e}")
        
    def validateToken(self, token):
        """
        Memvalidasi token JWT dari request (biasanya dari cookie).

        Args:
            token (str): Token JWT yang akan divalidasi.

        Returns:
            dict: Payload hasil decode JWT jika token valid.
                Contoh:
                {
                    "_id": "652ca8f17c8b83b4567abcd",
                    "name": "John Doe",
                    "role": "manager",
                    "iat": 1739518200,
                    "exp": 1739561400
                }

        Raises:
            Exception: Jika token tidak valid, kadaluarsa, atau tidak ditemukan.

        ---
        ✅ Contoh Output Berhasil:
        {'_id': '652ca8f17c8b83b4567abcd', 'name': 'John Doe', 'role': 'manager', 'iat': 1739518200, 'exp': 1739561400}

        ❌ Contoh Output Gagal:
        Exception: Token expired
        Exception: Invalid token
        Exception: Token not valid
        """
        try:
            token_data = self.repo.getData(query={"token": token})
            if token_data is None:
                return {"status": False, "message": "Token not found"}

            validate = jwt.decode(token_data["token"], Config.JWT_SECRET_KEY, algorithms=["HS256"], )
            return {"status": True, "message": "Token valid", "data": validate}
        except jwt.ExpiredSignatureError:
            self.deleteToken(token)
            print("Token expired")
            raise jwt.ExpiredSignatureError("Token expired")
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError("Invalid token")
        except Exception as e:
            raise Exception(f"Failed to validate token: {e}")
        
    def deleteToken(self, token):
        """
        Menghapus token dari database dan menghapus cookie 'token' di response.

        Args:
            token (str): Token JWT yang akan dihapus.

        Returns:
            dict: Hasil operasi penghapusan dari database.
                Contoh: {"deleted_count": 1}

        Raises:
            Exception: Jika token gagal dihapus dari database.

        ---
        ✅ Contoh Output Berhasil:
        {"message": "Successfully logout"}

        ❌ Contoh Output Gagal:
        Exception: Failed to delete token
        """
        try:
            delete = self.repo.deleteData(query={"token": token})
            if not delete.acknowledged:
                raise Exception("Failed to delete token")

            return delete.acknowledged
        except Exception as e:
            raise Exception(f"Something went wrong when deleting token: {e}")
        
    def checkAccess(self, accessRole=[], token=None):
        """
        Memeriksa apakah pengguna memiliki hak akses berdasarkan role-nya.

        Args:
            accessRole (list): Daftar role yang diizinkan.
                Contoh: ["owner", "manager"]
            token (str, optional): Token JWT yang digunakan untuk validasi.

        Returns:
            dict | bool:
                - dict: Payload JWT jika role diizinkan.
                - False: Jika role tidak diizinkan atau token tidak valid.

        ---
        ✅ Contoh Output Berhasil:
        {
            "_id": "652ca8f17c8b83b4567abcd",
            "name": "John Doe",
            "role": "manager",
            "iat": 1739518200,
            "exp": 1739561400
        }

        ❌ Contoh Output Gagal:
        False
        Exception: Token expired
        Exception: Invalid token
        """
        try:
            if token is None:
                return {"status": False, "message": "No token found"}


            currentUser = self.validateToken(token)
            if currentUser["data"]["role"] not in accessRole:
                return {"status": False, "message": "Forbidden"}
            response = {
                "status": True,
                "message": "Success",
                "data" : currentUser["data"]
            }
            return response
        except jwt.ExpiredSignatureError:
            self.deleteToken(token)
            return {"status": False, "message": "Token expired"}
        except jwt.InvalidTokenError:
            return {"status": False, "message": "Invalid token"}
        except Exception as e:
            print("AUTH ERROR:", e)
            return {"status": False, "message": "Invalid token"}
