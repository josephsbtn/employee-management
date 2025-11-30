from flask import Blueprint, render_template, request, redirect, jsonify
from service.storeService import StoreService
from utils.jwtHandler import SessionService
from utils.utility import Utility

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
        return redirect("/notHaveAccess")
    if currentUser["data"]["role"] == "manager":
        return jsonify({"status": True, "message": "Manager Branch", "data" : [{"branchId": currentUser["data"]["branchId"]}]}), 200
    data = service.getAllStore()
    print("[INFO] Data:", data)
    return jsonify(data), 200

    
@branchRoutesBp.route("/<id>", methods=["GET"])
def branchById(id):
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["owner"], token)
    print("CURRENT USER:", currentUser)
    if currentUser['status'] == False:
        return  redirect("/notHaveAccess")
    
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
        return redirect("notHaveAccess.html")
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
