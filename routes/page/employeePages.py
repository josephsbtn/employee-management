from flask import blueprints, render_template, request, redirect
from utils.jwtHandler import SessionService


EmployeePageBp = blueprints.Blueprint("EmployeePageBp", __name__)


@EmployeePageBp.route("/history", methods=["GET"])
def historyAttendance():
    try:
        token = request.cookies.get("token")
        currentUser = SessionService().checkAccess(["employee"], token)
        if currentUser['status'] == False:
            return redirect("/notHaveAccess")
        return render_template("employee/attendanceHistory.html")
    except Exception as e:
        return redirect("/")    

@EmployeePageBp.route("/leave-request", methods=["GET"])
def annualRequest():
    try:
        token = request.cookies.get("token")
        currentUser = SessionService().checkAccess(["employee", "manager"], token)
        if currentUser['status'] == False:
            return redirect("/notHaveAccess")
        return render_template("employee/leaveRequest.html")
    except Exception as e:
        return redirect("/")