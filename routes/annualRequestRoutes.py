from flask import Blueprint, render_template, request, redirect, jsonify, make_response, url_for
from service.annualRequestService import AnnualRequestService
from utils.jwtHandler import SessionService
from validation.fileValidation import FileValidation
import os
import random
import pendulum
import json

annualRequestBp = Blueprint("annualRequestBp", __name__)
service = AnnualRequestService()
session = SessionService()


@annualRequestBp.route("/request", methods=["POST"])
def annualRequest():
    print("-----------[ANNUAL REQUEST]-----------")
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["manager", "employee"], token)
    
    if currentUser['status'] == False:
        return redirect("/notHaveAccess")
        
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
        return redirect("/notHaveAccess")
    
    result = service.listAnnualByEmployee(id=currentUser["data"]["_id"])
    return jsonify(result), 200

@annualRequestBp.route("/list-manager", methods=["GET"])
def listRequest():
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["manager", "employee"], token)

    if currentUser['status'] == False:
        return redirect("/notHaveAccess")
    
    result = service.getRequestByBranch(currentUser=currentUser["data"])
    return jsonify(result), 200

@annualRequestBp.route("/detail/<request_id>", methods=["GET"])
def detailRequest(request_id):
    print("-----------[DETAIL ANNUAL REQUEST]-----------")
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["manager", "employee"], token)
    if currentUser['status'] == False:
        return redirect("/notHaveAccess")
    
    result = service.details(id=request_id)
    return jsonify(result), 200

@annualRequestBp.route("/cancel/<request_id>", methods=["PUT"])
def cancelRequest(request_id):
    print("-----------[CANCEL ANNUAL REQUEST]-----------")
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["manager", "employee"], token)
    if currentUser['status'] == False:
        return redirect("/notHaveAccess")
    result = service.cancelRequest(id=request_id, currentUser=currentUser["data"])
    return jsonify(result), 200 

@annualRequestBp.route("/approve/<request_id>", methods=["PUT"])
def approveRequest(request_id):
    print("-----------[APPROVE ANNUAL REQUEST]-----------")
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["manager", "employee"], token)
    if currentUser['status'] == False:
        return redirect("/notHaveAccess")
    data = request.get_json()
    result = service.approveRequest(id=request_id, currentUser=currentUser["data"], data=data)
    return jsonify(result), 200

@annualRequestBp.route("/reject/<request_id>", methods=["PUT"])
def rejectRequest(request_id):
    print("-----------[REJECT ANNUAL REQUEST]-----------", request_id)
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["manager", "employee"], token)
    if currentUser['status'] == False:
        return redirect("/notHaveAccess")
    data = request.get_json()
    result = service.rejectRequest(id=request_id, currentUser=currentUser["data"],data=data )
    return jsonify(result), 200