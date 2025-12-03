from flask import Blueprint, render_template, request, redirect, jsonify, make_response, url_for
from service.attendanceService import AttendanceService
from utils.jwtHandler import SessionService

"""
=================================================================================
ATTENDANCE & SHIFT MANAGEMENT API - DOKUMENTASI
=================================================================================

MODULE: Manajemen Kehadiran & Shift Karyawan

AUTENTIKASI:
- Semua endpoint memerlukan JWT token di cookies
- Validasi menggunakan SessionService.checkAccess()

AUTHORIZATION:
- Manager: Kelola shift, lihat kehadiran cabang, clock in/out
- Employee: Clock in/out, lihat jadwal sendiri

FITUR UTAMA:
- Clock In/Out karyawan dengan geolokasi
- Set & update shift harian (day/night shift)
- Remove karyawan dari shift
- Laporan kehadiran harian per cabang
- Laporan shift bulanan
- Summary kehadiran bulanan
- Jadwal shift karyawan

ENDPOINTS:
1. GET  /<date>                 → Kehadiran harian per cabang
2. POST /clockIn                → Clock in karyawan
3. POST /clockOut               → Clock out karyawan
4. POST /setShift               → Set shift harian (day/night)
5. PUT  /update/<id>            → Update shift
6. PUT  /remove/<id>            → Remove karyawan dari shift
7. GET  /getMonthlyShifts/<date> → Laporan shift bulanan
8. GET  /getMonthlySummary/<date> → Summary kehadiran bulanan
9. GET  /schedule/<employeeId>  → Jadwal shift karyawan

FORMAT RESPONSE:
Success: {"status": true, "message": "...", "data": {...}}
Error:   {"status": false, "message": "..."}

NOTES:
- Date format: YYYY-MM-DD atau YYYY-MM
- Manager hanya bisa kelola shift di cabangnya sendiri
- Clock in/out memerlukan data lokasi (latitude, longitude)

=================================================================================
"""

attendanceBp = Blueprint("attendanceBp", __name__)
service = AttendanceService()
session = SessionService()


@attendanceBp.route("/<date>", methods=["GET"])
def attendance(date=None):
    print("[ATTENDANCE ROUTES ]DATE:", date)
    token = request.cookies.get("token")
    currentUser = SessionService().checkAccess(["manager"], token)
    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    branchId = currentUser["data"]["branchId"]
    data = service.getAttendanceByStore(date=date, storeId=branchId)
    return jsonify(data), 200

@attendanceBp.route("/clockIn", methods=["POST"])
def attendanceClockIn():
    token = request.cookies.get("token")
    currentUser = SessionService().checkAccess(["employee", "manager"], token)
    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    req = request.get_json()
    data = service.employeeClockIn(data=req, employee=currentUser["data"])
    return jsonify(data), 200


# """_setShift_
#     data = {
#         "dayShift" = [
#             {"employeeId": employeeId,}
#         ],
#         "nightShift" = [
#             {"employeeId": employeeId,}
#         ]
#     }

# Returns:
#     _type_: _description_
# """
@attendanceBp.route("/setShift", methods=["POST"])
def setShift():
    token = request.cookies.get("token")
    currentUser = SessionService().checkAccess(["manager"], token)
    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    req = request.get_json()
    req["branchId"] = currentUser["data"]["branchId"]
    data = service.setShift(data=req, currentUser= currentUser["data"])
    return jsonify(data), 201

# @attendanceBp.route("/changeShift", methods=["PUT"])
# def changeShift():
#     token = request.cookies.get("token")
#     currentUser = SessionService().checkAccess(["manager"], token)
#     if currentUser['status'] == False:
#         return render_template("notHaveAccess.html")
#     req = request.get_json()
#     data = service.changeShift(data=req, employee=currentUser["data"])
#     print("[INFO] Data:", data)
#     return jsonify(data), 200

@attendanceBp.route("/clockOut", methods=["POST"])
def clockOut():
    token = request.cookies.get("token")
    currentUser = SessionService().checkAccess(["employee", "manager"], token)
    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    req = request.get_json()
    data = service.employeeClockOut(data=req, employee=currentUser["data"] )
    return jsonify(data), 200


@attendanceBp.route("/remove/<id>", methods=["PUT"])
def removeShift(id):
    print("-----------[REMOVE SHIFT ROUTES] ID:", id)
    token = request.cookies.get("token")
    currentUser = SessionService().checkAccess(["manager"], token)
    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    print("[INFO REMOVE SHIFT ROUTESS] ID:", id)
    req = request.get_json()
    data = service.removeShift(data=req, id=id, employee=currentUser["data"])
    return jsonify(data), 200


@attendanceBp.route("/update/<id>", methods=["PUT"])
def addEmployee(id):
    token = request.cookies.get("token")
    currentUser = SessionService().checkAccess(["manager"], token)
    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    req = request.get_json()
    data = service.updateShift(data=req, id=id, employee=currentUser["data"])
    return jsonify(data), 200


@attendanceBp.route("/getMonthlyShifts/<date>", methods=["GET"])
def getMonthlyShifts(date):
    token = request.cookies.get("token")
    currentUser = SessionService().checkAccess(["manager"], token)
    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    year = date.split("-")[0]
    month = date.split("-")[1]
    data = service.getMonthlyShifts(branchId=currentUser["data"]["branchId"], month=month, year=year)
    return jsonify(data), 200


@attendanceBp.route("/getMonthlySummary/<date>", methods=["GET"])
def getMonthlySummary(date):
    token = request.cookies.get("token")
    currentUser = SessionService().checkAccess(["manager"], token)
    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    print("[INFO] DATE:", date)
    year = date.split("-")[0]
    month = date.split("-")[1]
    data = service.getMonthlySummary(branchId=currentUser["data"]["branchId"], month=month, year=year)
    return jsonify(data), 200


@attendanceBp.route("/schedule/<employeeId>", methods=["GET"])
def getSchedule(employeeId):
    print("============[INFO] EMPLOYEE ID GET EMPLOYEE SCHEDULE : ==========", employeeId)
    token = request.cookies.get("token")
    currentUser = SessionService().checkAccess(["employee"], token)
    if currentUser['status'] == False:
        response = make_response(jsonify({"status": False, "message": "You don't have access"}), 403)
        return response
    branchId = currentUser["data"]["branchId"]
    data = service.getEmployeeSchedule(branchId=branchId, employeeId=employeeId)
    return jsonify(data), 200