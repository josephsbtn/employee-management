from flask import Blueprint, render_template, request, redirect, jsonify, make_response, url_for
from service.leaveRequestService import LeaveRequestService
from utils.jwtHandler import SessionService
from validation.fileValidation import FileValidation
import os
import random
import pendulum
import json

"""
=================================================================================
LEAVE REQUEST MANAGEMENT API - DOKUMENTASI
=================================================================================

MODULE: Manajemen Permohonan Cuti Karyawan

AUTENTIKASI:
- Semua endpoint memerlukan JWT token di cookies
- Validasi menggunakan SessionService.checkAccess()

AUTHORIZATION:
- Owner: Approve/reject semua request, lihat semua request
- Manager: Approve/reject request cabang, lihat request cabang, buat request
- Employee: Buat request, lihat request sendiri, cancel request sendiri

FITUR UTAMA:
- Buat permohonan cuti (annual leave)
- Upload attachment (opsional)
- Lihat daftar request (employee/manager/owner)
- Detail request
- Approve/reject request (manager/owner)
- Cancel request (employee/manager)

ENDPOINTS:
1. POST /request                    → Buat permohonan cuti
2. GET  /list-employee              → Daftar request karyawan (pribadi)
3. GET  /list-manager               → Daftar request untuk manager/owner
4. GET  /detail/<request_id>        → Detail request
5. PUT  /approve/<request_id>       → Approve request
6. PUT  /reject/<request_id>        → Reject request
7. PUT  /cancel/<request_id>        → Cancel request

FORMAT REQUEST:
- POST /request:
  {
    "type": "annual",
    "startDate": "YYYY-MM-DD",
    "endDate": "YYYY-MM-DD",
    "reason": "Alasan cuti",
    "attachment": file (optional)
  }

- PUT /approve/<request_id>:
  {
    "approvalNote": "Catatan persetujuan (optional)"
  }

- PUT /reject/<request_id>:
  {
    "rejectionNote": "Alasan penolakan"
  }

FORMAT RESPONSE:
Success: {"status": true, "message": "...", "data": {...}}
Error:   {"status": false, "message": "...", "errors": {...}}

NOTES:
- File attachment disimpan di ./uploads/annualAttachment/
- Format file: ANNUAL-XXYYYYMMDDHHMMSS.ext
- Request ID format: ANNUAL-XXYYYYMMDDHHMMSS
- Manager hanya bisa approve/reject request di cabangnya
- Owner bisa approve/reject semua request

FILE UPLOAD:
- Supported formats: jpg, jpeg, png, pdf, doc, docx
- Max size ditentukan di FileValidation
- File disimpan dengan nama unik untuk menghindari konflik

=================================================================================
"""

annualRequestBp = Blueprint("annualRequestBp", __name__)
service = LeaveRequestService()
session = SessionService()


@annualRequestBp.route("/request", methods=["POST"])
def annualRequest():
    print("-----------[ANNUAL REQUEST]-----------")
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["manager", "employee"], token)
    
    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
        
    directory = "./uploads/annualAttachment"
    os.makedirs(directory, exist_ok=True)
    
    file = request.files.get('attachment', None)
    fileUrl = ""
    fileName = ""
    validatedFile = None
    _id = "ANNUAL-" + str(random.randint(10, 99)) + str(pendulum.now().format('YYYYMMDDHHmmss'))
    
    if file and file.filename:
        validatedFile = FileValidation(file).validation()
        fileName = validatedFile["fileName"]
        filename = _id + f".{validatedFile['fileType']}"
        file.save(os.path.join(directory, filename))
        fileUrl = f"{request.url_root}uploads/annualAttachment/{filename}"
        print(f"[INFO] File uploaded: {filename}")
    else:
        print("[INFO] No file uploaded")
    
    if request.is_json:
        data = request.get_json()
        print("[INFO ANNUAL REQUEST] Data from JSON:", data)
    elif request.form.get("payload"):
        data = json.loads(request.form.get("payload"))
        print("[INFO ANNUAL REQUEST] Data from payload:", data)
    else:
        data = {
            "type": request.form.get("type"),
            "startDate": request.form.get("startDate"),
            "endDate": request.form.get("endDate"),
            "reason": request.form.get("reason")
        }
        print("[INFO ANNUAL REQUEST] Data from form fields:", data)
    
    data["attachmentUrl"] = fileUrl
    data["fileName"] = fileName
    data["employeeId"] = currentUser["data"]["_id"]
    
    print("[ANNUAL REQUEST] Final data:", data)
    
    result = service.createAnnualRequest(data=data, currentUser=currentUser["data"])
    return jsonify(result), 200


@annualRequestBp.route("/list-employee", methods=["GET"])
def listAnnualRequest():
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["manager", "employee"], token)

    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    
    result = service.listAnnualByEmployee(id=currentUser["data"]["_id"])
    return jsonify(result), 200

@annualRequestBp.route("/list-manager", methods=["GET"])
def listRequest():
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["manager", "owner"], token)

    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    if currentUser["data"]["role"] == "owner":
        result = service.getRequestByOwner()
        return jsonify(result), 200
    result = service.getRequestByBranch(currentUser=currentUser["data"])
    return jsonify(result), 200

@annualRequestBp.route("/detail/<request_id>", methods=["GET"])
def detailRequest(request_id):
    print("-----------[DETAIL ANNUAL REQUEST]-----------")
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["manager", "employee", "owner"], token)
    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    
    result = service.details(id=request_id)
    return jsonify(result), 200

@annualRequestBp.route("/cancel/<request_id>", methods=["PUT"])
def cancelRequest(request_id):
    print("-----------[CANCEL ANNUAL REQUEST]-----------")
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["manager", "employee"], token)
    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    result = service.cancelRequest(id=request_id, currentUser=currentUser["data"])
    return jsonify(result), 200 

@annualRequestBp.route("/approve/<request_id>", methods=["PUT"])
def approveRequest(request_id):
    print("-----------[APPROVE ANNUAL REQUEST]-----------")
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["manager", "owner"], token)
    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    data = request.get_json()
    result = service.approveRequest(id=request_id, currentUser=currentUser["data"], data=data)
    return jsonify(result), 200

@annualRequestBp.route("/reject/<request_id>", methods=["PUT"])
def rejectRequest(request_id):
    print("-----------[REJECT ANNUAL REQUEST]-----------", request_id)
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["manager", "owner"], token)
    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    data = request.get_json()
    result = service.rejectRequest(id=request_id, currentUser=currentUser["data"],data=data )
    return jsonify(result), 200