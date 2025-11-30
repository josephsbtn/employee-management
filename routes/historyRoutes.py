from flask import Blueprint, render_template, request, jsonify, redirect, make_response
from service.historyService import HistoryService
from utils.jwtHandler import SessionService

historyRoutesBp = Blueprint("historyRoutesBp", __name__)
service = HistoryService()
session = SessionService()

@historyRoutesBp.route("/all", methods=["GET"])
def getAllHistory():
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["owner"], token)
    print("CURRENT USER:", currentUser)
    if currentUser['status'] == False:
        response = make_response(redirect("/notHaveAccess"))
        response.delete_cookie("token")
        return redirect("/notHaveAccess")
    data = service.getAllHistory()
    return jsonify(data), 200

@historyRoutesBp.route("/all/user", methods=["GET"])
def getUserHistory():
    print("-----------[GET USER HISTORY]-----------")
    token = request.cookies.get("token")
    currentUser = session.checkAccess(["owner", "manager", "employee"], token)
    if currentUser['status'] == False:
        response = make_response(redirect("/notHaveAccess"))
        response.delete_cookie("token")
        return redirect("/notHaveAccess")
    print("OTW KE SERVICE")
    data = service.getUserHistory(currentUser["data"]["_id"])
    return jsonify(data), 200