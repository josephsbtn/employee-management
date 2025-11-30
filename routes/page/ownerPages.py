from flask import Blueprint, render_template, request, redirect, jsonify
from utils.jwtHandler import SessionService

OwnerPageBp = Blueprint("OwnerPageBp", __name__)

@OwnerPageBp.route("/branch-manage", methods=["GET"])
def branchManage():
    try:
        token = request.cookies.get("token")
        currentUser = SessionService().checkAccess(["owner"], token)
        print("CURRENT USER:", currentUser)
        if currentUser['status'] == False:
            return render_template("notHaveAccess.html")
        return render_template("owner/branchManage.html")
    except Exception as e:
        print("[ERROR] Unexpected error:", e)
        return redirect("/")
@OwnerPageBp.route("/branch-performance/<id>", methods=["GET"])
def branchPerformance():
    try:
        token = request.cookies.get("token")
        currentUser = SessionService().checkAccess(["owner"], token)
        print("CURRENT USER:", currentUser)
        if currentUser['status'] == False:
            return render_template("notHaveAccess.html")
        return render_template("branchPerformance.html")
    except Exception as e:
        return redirect("/")

@OwnerPageBp.route("/history", methods=["GET"])
def history():
    try:
        token = request.cookies.get("token")
        currentUser = SessionService().checkAccess(["owner", "manager", "employee"], token)
        print("CURRENT USER:", currentUser)
        if currentUser['status'] == False:
            return render_template("notHaveAccess.html")
        return render_template("owner/historyLog.html")
    except Exception as e:
        return redirect("/")