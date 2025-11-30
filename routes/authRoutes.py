from flask import Blueprint, request, redirect, jsonify, make_response, url_for
from service.employeeService import EmployeeService
from utils.jwtHandler import SessionService
from utils.utility import Utility

authBp = Blueprint("authBp", __name__)
employService = EmployeeService()
session = SessionService()
utility = Utility()

@authBp.route("/login", methods=["POST"])
def login():
    """
    Endpoint untuk login user.
    
    Menerima data login dalam format JSON, melakukan sanitasi data,
    memvalidasi kredensial, dan mengembalikan token dalam cookie.
    
    Request Body (JSON):
        - username/email: Kredensial login user
        - password: Password user
    
    Returns:
        Response (JSON):
            - status (bool): Status keberhasilan login
            - message (str): Pesan response
        
        Cookie:
            - token: JWT token untuk autentikasi
    
    Status Codes:
        - 200: Login berhasil
        - 400: Login gagal (kredensial salah atau data tidak valid)
    
    Example:
        POST /login
        {
            "username": "john@aventra.com",
            "password": "password123"
        }
    """
    data = request.get_json()
    result = employService.login(data)
    if not result.get("status"):
        return jsonify(result), 400
    token = result.get("token")
    response = make_response(jsonify({
        "status": True,
        "message": "Successfully login"
    }), 200)
    response.set_cookie('token', token)
    redirect(url_for("pageBp.dashboard"))
    return response
    
    
@authBp.route("/current", methods=["GET"])
def currentUser():
    """
    Endpoint untuk mendapatkan informasi user yang sedang login.
    
    Memvalidasi token dari cookie dan mengembalikan data user
    jika memiliki akses yang valid (owner, manager, atau employee).
    
    Headers:
        Cookie: token - JWT token untuk autentikasi
    
    Returns:
        Response (JSON):
            - Jika berhasil: Data user yang sedang login
            - Jika gagal: 
                - status (bool): False
                - message (str): Pesan error
    
    Status Codes:
        - 200: Berhasil mendapatkan data user
        - 400: Token tidak ditemukan
        - 403: Token tidak valid atau akses ditolak
        - 500: Server error
    
    Example:
        >>> GET /current
        >>> Cookie: token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        >>> Response: {
        >>>     "id": "123",
        >>>     "username": "john",
        >>>     "role": "employee"
        >>> }
    """
    try:
        token = request.cookies.get("token")
        if not token:
            return jsonify({"status": False, "message": "No token found"}), 400
        result = session.checkAccess(["owner", "manager", "employee"], token)
        if result["status"] == False:
           return redirect("/notHaveAccess"), 403
        return jsonify(result["data"]), 200
    except Exception as e:
        return jsonify({"message": "error", "error": str(e)}), 500

@authBp.route("/logout", methods=["POST"])
def logout():
    """
    Endpoint untuk logout user.
    
    Menghapus token dari sistem dan menghapus cookie token
    dari browser user.
    
    Headers:
        Cookie: token - JWT token yang akan dihapus
    
    Returns:
        Response (JSON):
            - status (bool): Status keberhasilan logout
            - message (str): Pesan response
    
    Status Codes:
        - 200: Logout berhasil
        - 400: Token tidak ditemukan atau gagal logout
        - 500: Server error
    
    Side Effects:
        - Menghapus token dari database/storage
        - Menghapus cookie 'token' dari browser
    
    Example:
        >>> POST /logout
        >>> Cookie: token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        >>> Response: {
        >>>     "status": true,
        >>>     "message": "Successfully logout"
        >>> }
    """
    try:
        token = request.cookies.get("token")
        print("TOKENN = ", token)
        if not token:
            return jsonify({"status": False, "message": "No token found"}), 400
        result = SessionService().deleteToken(token=token)
        if not result:
            return jsonify({"status": False, "message": "Failed to logout"}), 400
        response = make_response(jsonify({"status": True, "message": "Successfully logout"}), 200)
        response.delete_cookie("token")
        return response
    except Exception as e:
        return jsonify({"message": "error", "error": str(e)}), 500
    
