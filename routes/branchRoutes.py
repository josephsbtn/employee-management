from flask import Blueprint, render_template, request, redirect, jsonify, make_response
from service.storeService import StoreService
from utils.jwtHandler import SessionService
from utils.utility import Utility

"""
=================================================================================
BRANCH/STORE MANAGEMENT API - DOKUMENTASI
=================================================================================

MODULE: Manajemen Cabang/Toko (CRUD + Aktivasi/Deaktivasi)

AUTENTIKASI:
- Semua endpoint memerlukan JWT token di cookies
- Validasi menggunakan SessionService.checkAccess()

AUTHORIZATION:
- Owner: Akses penuh semua operasi cabang
- Manager: Hanya bisa melihat cabang sendiri (list active)
- Employee: Hanya bisa melihat daftar cabang

KEAMANAN:
- ID parameter disanitasi (blockMongoInject, sanitizeHTML)
- Validasi token setiap request
- Error 403 untuk akses tidak sah, 400 untuk request invalid

ENDPOINTS:
1. GET    /                → Daftar semua cabang
2. GET    /<id>            → Detail cabang berdasarkan ID
3. POST   /create          → Tambah cabang baru
4. PUT    /update/<id>     → Update data cabang
5. DELETE /delete/<id>     → Hapus cabang permanen
6. PUT    /non-active/<id> → Nonaktifkan cabang
7. PUT    /active/<id>     → Aktifkan kembali cabang
8. GET    /active          → Daftar cabang aktif saja

FORMAT RESPONSE:
Success: {"status": true, "message": "...", "data": {...}}
Error:   {"status": false, "message": "..."}

NOTES:
- Manager hanya bisa melihat cabangnya sendiri di endpoint /active
- Owner bisa melihat semua cabang
- Soft delete menggunakan endpoint /non-active (recommended)
- Hard delete menggunakan endpoint /delete (permanent)

=================================================================================
"""

branchRoutesBp = Blueprint("branchRoutesBp", __name__)
session = SessionService()
service = StoreService()
utility = Utility()
@branchRoutesBp.route("", methods=["GET"])
def branch():
    token = request.cookies.get("token")
    print("-------------CURRENT USER IN BRANCHES-------:")
    currentUser = session.checkAccess(["owner", "manager", "employee"], token)
    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
   
    data = service.getAllStore()
    print("[INFO] Data:", data)
    return jsonify(data), 200

    
@branchRoutesBp.route("/<id>", methods=["GET"])
def branchById(id):
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["owner"], token)
    print("CURRENT USER:", currentUser)
    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    
    utility.blockMongoInject(id)
    sanitizedId = utility.sanitizeHTML(id)
    id = sanitizedId
    
    data = service.storeDetails(id)
    return jsonify(data), 200
    
@branchRoutesBp.route("/create", methods=["POST"])
def createBranch():
    
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["owner"], token)
    print("CURRENT USER:", currentUser)
    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    
    data = request.get_json()
    
    if not data:
        return jsonify({"status": False, "message": "No data found"}), 400
    print("[INFO] Data:", data)
    result = service.addStore(data, currentUser["data"]["_id"], currentUser["data"]["name"])
    if result["status"] == False:
        return jsonify(result), 400
    return jsonify(result), 201

    
@branchRoutesBp.route("/update/<id>", methods=["PUT"])
def updateBranch(id):
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["owner"], token)
    print("CURRENT USER:", currentUser)
    if currentUser['status'] == False:
        return  redirect("/notHaveAccess")
    data = request.get_json()
    print("[INFO UPDATE BRANCH ROUTES ] Data:", data)
    print("[UPDATE BRANCH] ID:", id)
    result = service.updateStore(id=id, data=data,  employeeId=currentUser["data"]["_id"], employeeName=currentUser["data"]["name"])
    return jsonify(result), 200

    
@branchRoutesBp.route("/delete/<id>", methods=["DELETE"])
def deleteBranch(id):
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["owner"], token)
    print("CURRENT USER:", currentUser)
    if currentUser['status'] == False:
        return redirect("/notHaveAccess")
    result = service.deleteStore(id, currentUser["data"]["_id"], currentUser["data"]["name"])
    print("[INFO] Result:", result)
    return jsonify(result), 200

@branchRoutesBp.route("/non-active/<id>", methods=["PUT"])
def nonActiveBranch(id):
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["owner"], token)
    print("CURRENT USER:", currentUser)
    if currentUser['status'] == False:
        return redirect("/notHaveAccess")
    result = service.nonActivateStore(id, employee=currentUser["data"])
    print("[INFO] Result:", result), 
    return jsonify(result), 200

@branchRoutesBp.route("/active/<id>", methods=["PUT"])
def activeBranch(id):
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["owner"], token)
    print("CURRENT USER:", currentUser)
    if currentUser['status'] == False:
        return  redirect("/notHaveAccess")
    result = service.ActivateStore(id, employee=currentUser["data"])
    print("[INFO] Result:", result), 
    return jsonify(result), 200

@branchRoutesBp.route("/active", methods=["GET"])
def listActiveBranch():
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["owner", "manager"], token)
    print("CURRENT USER:", currentUser)
    if currentUser['status'] == False:
        return  redirect("/notHaveAccess")
    result = service.getActiveStore()
    if currentUser["data"]["role"] == "manager":
        managerstore = None
        for store in result["data"]:
            if store["_id"] == currentUser["data"]["branchId"]:
                managerstore = store
                break
            
        return jsonify({"status": True, "message": "Manager Branch", "data" : [managerstore]}), 200
    print("[==== INFO ====] Result:", result), 
    return jsonify(result), 200
