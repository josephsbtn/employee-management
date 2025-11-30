from flask import Blueprint, request, jsonify, render_template, redirect
from service.employeeService import EmployeeService
from utils.jwtHandler import SessionService
from utils.utility import Utility
employeesBp = Blueprint("employeesBp", __name__)
service = EmployeeService()
session = SessionService()
utility = Utility()

@employeesBp.route("/all", methods=["GET"])
def allEmployees():
    """Get all employees

    Endpoint:
        GET /employees/all

    Description:
        Mengambil semua data karyawan dari database.

    Returns:
        __object__: {
            "status": True,
            "message": "Data fetched successfully",
            "data": [
                {
                    "_id": "string",
                    "name": "string",
                    "email": "string",
                    "status": "string",
                    "role": "string"
                }
            ]
        }

    Raises:
        Exception: Jika terjadi kesalahan saat pengambilan data.
    """
    token = request.cookies.get("token")
    if not token:
        return jsonify({"status": False, "message": "No token found"}), 400
    result = session.checkAccess(["owner", "manager"], token)
    print("[INFO] Result jtw get all employee:", result)
    if result["status"] == False:
        return jsonify(result), 403
    if result["data"]["role"] == "manager":
        print("[INFO] Branch ID IN GET ALL EMPLOYEES:", result["data"]["branchId"])
        data = service.getAllEmployee(result["data"]["branchId"])
    else: 
        data = service.getAllEmployee()
            
    return jsonify(data), 200


@employeesBp.route("/create", methods=["POST"])
def createEmployee():
    """Create new employee

    Endpoint:
        POST /employees/create

    Description:
        Menambahkan data karyawan baru ke dalam database.

    Request Body:
        __object__: {
            "name": "string",
            "email": "string",
            "password": "string",
            "status": "string",
            "role": "string",
            "branchId": "string",
            "salary": Number
        }

    Returns:
        __object__: {
            "status": True,
            "message": "Data inserted successfully",
            "data": {
                "inserted_id": "string"
            }
        }

    Raises:
        ValidationError: Jika data request tidak sesuai dengan schema validasi.
        Exception: Jika proses penyimpanan data gagal.
    """
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["owner", "manager"], token)
    if currentUser['status'] == False:
        return redirect("/notHaveAccess")
    
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
    """Update employee data

    Endpoint:
        PUT /employees/update/<id>

    Description:
        Memperbarui data karyawan berdasarkan ID.

    Path Parameters:
        id (string): ID dari karyawan yang akan diperbarui.

    Request Body:
        __object__: {
            "name": "string",
            "email": "string",
            "status": "string",
            "role": "string",
            "branchId": "string",
            "salary": Number
        }

    Returns:
        __object__: {
            "status": True,
            "message": "Data updated successfully",
            "data": {
                "matched_count": int,
                "modified_count": int
            }
        }

    Raises:
        ValidationError: Jika data tidak sesuai schema validasi.
        Exception: Jika update data gagal.
    """
    token = request.cookies.get("token")
    if not token:
        return jsonify({"status": False, "message": "No token found"}), 400
    result = session.checkAccess(["owner", "manager"], token)
    if result["status"] == False:
        return jsonify(result), 403
    
    utility.blockMongoInject(id)
    sanitizedId = utility.sanitizeHTML(id)
    id = sanitizedId
    
    data = request.get_json()
    
    if not data:
        return jsonify({"status": False, "message": "No data found"}), 400
    
    updateData = service.updateEmploye(data, id, result["data"])
    if not updateData.get("status"):
        return jsonify(updateData), 400
    return jsonify(updateData), 200


@employeesBp.route("/fire/<id>", methods=["PUT"])
def fireEmployee(id):
    """Deactivate (fire) an employee

    Endpoint:
        DELETE /employees/fire/<id>

    Description:
        Mengubah status karyawan menjadi "inactive" berdasarkan ID.
        Hanya dapat dilakukan oleh pengguna yang sudah memiliki token valid.

    Path Parameters:
        id (string): ID dari karyawan yang akan dinonaktifkan.

    Cookie:
        token (string): Token autentikasi JWT.

    Returns:
        __object__: {
            "status": True,
            "message": "Data deleted successfully",
            "data": {
                "matched_count": int,
                "modified_count": int
            }
        }

    Raises:
        Exception: Jika proses penghapusan data gagal.
    """
    print("[INFO ROUTES] GET TOKEN FIRE EMPLOYEE")
    token = request.cookies.get("token")
    print("token : ", token)
    if not token:
        return jsonify({"status": False, "message": "No token found"}), 400
    result = session.checkAccess(["owner", "manager"], token)
    if result["status"] == False:
        return jsonify(result), 403
    
    utility.blockMongoInject(id)
    sanitizedId = utility.sanitizeHTML(id)
    id = sanitizedId
    
    fireData = service.fireEmployee(employee=result["data"], id=id)
    if not fireData.get("status"):
        return jsonify(fireData), 400
    print("fireData: ", fireData)
    return jsonify(fireData), 200

@employeesBp.route("/<id>", methods=["GET"])
def employeeDetails(id):
    token = request.cookies.get("token")
    if not token:
        return jsonify({"status": False, "message": "No token found"}), 400
    result = session.checkAccess(["owner", "manager", "employee"], token)
    if result["status"] == False:
        return jsonify(result), 403
    
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
    result = session.checkAccess(["owner", "manager"], token)
    if result["status"] == False:
        return jsonify(result), 403
    
    utility.blockMongoInject(id)
    sanitizedId = utility.sanitizeHTML(id)
    id = sanitizedId
    
    data = service.deleteEmployee( id=id, employee=result["data"] )
    return jsonify(data), 200

@employeesBp.route("/activate/<id>", methods=["PUT"])
def  activateEmployee(id):
    token = request.cookies.get("token")
    if not token:
        return jsonify({"status": False, "message": "No token found"}), 400
    result = session.checkAccess(["owner", "manager"], token)
    if result["status"] == False:
        return jsonify(result), 403
    
    sanitizedId = utility.blockMongoInject(id)
    sanitizedId = utility.sanitizeHTML(sanitizedId)
    id = sanitizedId
    
    data = service.activateEmployee(id=id, employee=result["data"])
    return jsonify(data), 200   

@employeesBp.route("/profile", methods=["GET"])
def employeeProfile():
    print("[INFO] MASUK EMPLOYEE PROFILE")
    token = request.cookies.get("token")
    if not token:
        return jsonify({"status": False, "message": "No token found"}), 400
    result = session.checkAccess(["owner", "manager", "employee"], token)
    if result["status"] == False:
        return redirect("/notHaveAccess")
   
       
    data = service.employeeProfile(result["data"])
    return jsonify(data), 200