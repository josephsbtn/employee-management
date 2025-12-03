from flask import Blueprint, request, jsonify, render_template, redirect, make_response
from service.employeeService import EmployeeService
from utils.jwtHandler import SessionService
from utils.utility import Utility

"""
=================================================================================
EMPLOYEE MANAGEMENT API - DOKUMENTASI
=================================================================================

MODULE: Manajemen Karyawan (CRUD + Aktivasi/Deaktivasi)

AUTENTIKASI:
- Semua endpoint memerlukan JWT token di cookies
- Validasi menggunakan SessionService.checkAccess()

AUTHORIZATION:
- Owner: Akses penuh semua data
- Manager: Hanya karyawan di cabang yang sama
- Employee: Hanya profil sendiri

KEAMANAN:
- ID parameter disanitasi (blockMongoInject, sanitizeHTML)
- Validasi token setiap request
- Error 403 untuk akses tidak sah, 400 untuk request invalid

ENDPOINTS:
1. GET    /all           → Daftar karyawan
2. POST   /create        → Tambah karyawan baru
3. PUT    /update/<id>   → Update data karyawan
4. PUT    /fire/<id>     → Nonaktifkan (soft delete)
5. DELETE /delete/<id>   → Hapus permanen (hard delete)
6. PUT    /activate/<id> → Aktifkan kembali
7. GET    /<id>          → Detail karyawan
8. GET    /profile       → Profil user login

FORMAT RESPONSE:
Success: {"status": true, "message": "...", "data": {...}}
Error:   {"status": false, "message": "..."}

=================================================================================
"""

employeesBp = Blueprint("employeesBp", __name__)
service = EmployeeService()
session = SessionService()
utility = Utility()



@employeesBp.route("/all", methods=["GET"])
def allEmployees():
    token = request.cookies.get("token")
    if not token:
        return jsonify({"status": False, "message": "No token found"}), 400
    result = session.checkAccess(["owner", "manager"], token)
    if result["status"] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    if result["data"]["role"] == "manager":
        print("[INFO] Branch ID IN GET ALL EMPLOYEES:", result["data"]["branchId"])
        data = service.getAllEmployee(result["data"]["branchId"])
    else: 
        data = service.getAllEmployee()
            
    return jsonify(data), 200


@employeesBp.route("/create", methods=["POST"])
def createEmployee():
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["owner", "manager"], token)
    if currentUser["status"] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    
    data = request.get_json()
    
    if not data:
        return jsonify({"status": False, "message": "No data found"}), 400
    
    if currentUser['data']['role'] == "manager":
        data['branchId'] = currentUser['data']['branchId']
    insertData = service.newEmployee(data, employee=currentUser["data"])
    if not insertData.get("status"):
        return jsonify(insertData), 400
    return jsonify(insertData), 200


@employeesBp.route("/update/<id>", methods=["PUT"])
def updateEmployee(id):
    token = request.cookies.get("token")
    if not token:
        return jsonify({"status": False, "message": "No token found"}), 400
    currentUser = session.checkAccess(["owner", "manager"], token)
    if currentUser["status"] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    
    utility.blockMongoInject(id)
    sanitizedId = utility.sanitizeHTML(id)
    id = sanitizedId
    
    data = request.get_json()
    
    if not data:
        return jsonify({"status": False, "message": "No data found"}), 400
    
    updateData = service.updateEmploye(data, id, currentUser["data"])
    if not updateData.get("status"):
        return jsonify(updateData), 400
    return jsonify(updateData), 200


@employeesBp.route("/fire/<id>", methods=["PUT"])
def fireEmployee(id):
    print("[INFO ROUTES] GET TOKEN FIRE EMPLOYEE")
    token = request.cookies.get("token")
    print("token : ", token)
    if not token:
        return jsonify({"status": False, "message": "No token found"}), 400
    currentUser = session.checkAccess(["owner", "manager"], token)
    if currentUser["status"] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    
    utility.blockMongoInject(id)
    sanitizedId = utility.sanitizeHTML(id)
    id = sanitizedId
    
    fireData = service.fireEmployee(employee=currentUser["data"], id=id)
    if not fireData.get("status"):
        return jsonify(fireData), 400
    print("fireData: ", fireData)
    return jsonify(fireData), 200

@employeesBp.route("/<id>", methods=["GET"])
def employeeDetails(id):
    token = request.cookies.get("token")
    if not token:
        return jsonify({"status": False, "message": "No token found"}), 400
    currentUser = session.checkAccess(["owner", "manager", "employee"], token)
    if currentUser["status"] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    
    utility.blockMongoInject(id)
    sanitizedId = utility.sanitizeHTML(id)
    id = sanitizedId
    
    data = service.getEmployeeById(id)
    return jsonify(data), 200
    
    
@employeesBp.route("/delete/<id>", methods=["DELETE"])
def deleteEmployee(id):
    token = request.cookies.get("token")
    if not token:
        return jsonify({"status": False, "message": "No token found"}), 400
    currentUser = session.checkAccess(["owner", "manager"], token)
    if currentUser["status"] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    
    utility.blockMongoInject(id)
    sanitizedId = utility.sanitizeHTML(id)
    id = sanitizedId
    
    data = service.deleteEmployee( id=id, employee=currentUser["data"] )
    return jsonify(data), 200

@employeesBp.route("/activate/<id>", methods=["PUT"])
def  activateEmployee(id):
    token = request.cookies.get("token")
    if not token:
        return jsonify({"status": False, "message": "No token found"}), 400
    currentUser = session.checkAccess(["owner", "manager"], token)
    if currentUser["status"] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    
    utility.blockMongoInject(id)
    sanitizedId = utility.sanitizeHTML(id)
    id = sanitizedId
    
    data = service.activateEmployee(id=id, employee=currentUser["data"])
    return jsonify(data), 200   

@employeesBp.route("/profile", methods=["GET"])
def employeeProfile():
    print("[INFO] MASUK EMPLOYEE PROFILE")
    token = request.cookies.get("token")
    if not token:
        return jsonify({"status": False, "message": "No token found"}), 400
    currentUser = session.checkAccess(["owner", "manager", "employee"], token)
    if currentUser["status"] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
       
    data = service.employeeProfile(currentUser["data"])
    return jsonify(data), 200