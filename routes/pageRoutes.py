from flask import Blueprint, render_template,make_response, request, redirect, jsonify, abort
from utils.jwtHandler import SessionService
from routes.page.ownerPages import OwnerPageBp
from routes.page.managerPages import ManagerPageBp
from routes.page.employeePages import EmployeePageBp
from utils.jwtHandler import SessionService

pageBp = Blueprint("pageBp", __name__)
checkAccess = SessionService().checkAccess()
pageBp.register_blueprint(OwnerPageBp, url_prefix="/owner")
pageBp.register_blueprint(ManagerPageBp, url_prefix="/manager")
pageBp.register_blueprint(EmployeePageBp, url_prefix="/employees")

        
@pageBp.route("/", methods=["GET"])
def index():
    """
    Halaman utama.
    Jika user sudah login (punya token valid) → redirect ke dashboard.
    Kalau belum login → tampilkan halaman login (authPage.html).
    """
    try:
        token = request.cookies.get("token")
        if token:
            currentUser = SessionService().validateToken(token)
            print("CURRENT USER:", currentUser)
            if currentUser["status"] == False:
                return render_template("authPage.html")
            return redirect("/dashboard")
        return render_template("authPage.html")
    except Exception as e:
        print("Token invalid atau expired:", e)

    return render_template("authPage.html")
        
@pageBp.route("/dashboard", methods=["GET"])
def dashboard():
    """
    Menentukan tampilan dashboard berdasarkan role user.
    Hanya role: owner, manager, atau employee yang diizinkan.
    """
    try:
        token = request.cookies.get("token")
        currentUser = SessionService().checkAccess(["owner", "manager", "employee"], token)
        print("CURRENT USER:", currentUser)
        if currentUser['status'] == False:
            return render_template("notHaveAccess.html")
        role = currentUser['data']['role']
        print("[INFO] Role:", role)
        print("CURRENT USER:", currentUser)

        if role == "owner":
            return render_template("owner/dashboardOwner.html")
        elif role == "manager":
            return render_template("manager/dashboardManager.html")
        elif role == "employee":
            return render_template("employee/dashboardEmployee.html")
        else:
            return jsonify({"status": False, "message": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"status": False, "message": "error", "error": str(e)}), 500

    
@pageBp.route("/employee-manage", methods=["GET"])
def employee():
    try:
        token = request.cookies.get("token")
        currentUser = SessionService().checkAccess(["owner", "manager", "employee"], token)
        print("CURRENT USER:", currentUser)
        if currentUser['status'] == False:
            return render_template("notHaveAccess.html")
        role = currentUser['data']['role']

        if role == "owner" or role == "manager":
            return render_template("/employeeManage.html")
        else :
            return 403
    except Exception as e:
        return jsonify({"message": "error", "error": str(e)}), 500
    
@pageBp.route("/profile", methods=["GET"])
def profile():
    try:
        token = request.cookies.get("token")
        currentUser = SessionService().checkAccess(["owner", "manager", "employee"], token)
        print("CURRENT USER:", currentUser)
        if currentUser['status'] == False:
            return render_template("notHaveAccess.html")
        return render_template("profileUser.html")
    except Exception as e:
        return jsonify({"message": "error", "error": str(e)}), 500
    
    
@pageBp.route("/notHaveAccess", methods=["GET"])
def notHaveAccess():
    return render_template("notHaveAccess.html")


    


