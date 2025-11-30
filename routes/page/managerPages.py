from flask import blueprints, render_template, request, redirect, jsonify
from utils.jwtHandler import SessionService

ManagerPageBp = blueprints.Blueprint("ManagerPageBp", __name__)
@ManagerPageBp.route("/shift-schedule", methods=["GET"])
def branchPerformance():
    try:
        token = request.cookies.get("token")
        currentUser = SessionService().checkAccess(["manager"], token)
        if currentUser['status'] == False:
            return redirect("/notHaveAccess")
        return render_template("manager/shiftManage.html")
    except Exception as e:
        return redirect("/")
    
@ManagerPageBp.route("/leave-request", methods=["GET"])
def annualRequest():
    try:
        token = request.cookies.get("token")
        currentUser = SessionService().checkAccess(["manager"], token)
        if currentUser['status'] == False:
            return redirect("/notHaveAccess")
        return render_template("manager/leaveRequestManage.html")
    except Exception as e:
        return redirect("/")