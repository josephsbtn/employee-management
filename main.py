from flask import Flask, jsonify, send_from_directory
from routes.employeesRoutes import employeesBp
from routes.pageRoutes import pageBp
from routes.authRoutes import authBp
from routes.branchRoutes import branchRoutesBp
from routes.attendanceRoutes import attendanceBp
from routes.historyRoutes import historyRoutesBp
from routes.annualRequestRoutes import annualRequestBp
from marshmallow import ValidationError

app = Flask(__name__)

@app.errorhandler(ValidationError)
def handle_validation_error(e):
    errors = getattr(e, "messages", str(e))
    print("====== [ ERRORS VALIDATION] ======")
    print(errors)
    payloadError = {
        "status": False,
        "message": "Validation error",
        "errors": errors.messages
    }
    print(payloadError)
    return jsonify(payloadError), 400

@app.errorhandler(ValueError)
def handle_value_error(e):
    print("====== [ ERRORS VALUE ] ======")
    print(e)
    return jsonify({"status": False,"message": "Error " + str(e), "error": str(e)}), 400
    
@app.errorhandler(Exception)
def error_handler(e):
    print("====== [ ERRORS ] ======")
    print("[ERROR] Unexpected error:", e)
    return jsonify({"status": False,"message": "Error " + str(e), "error": str(e)}), 500
    
@app.route("/uploads/annualAttachment/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory("./uploads/annualAttachment", filename)



app.register_blueprint(authBp, url_prefix="/auth")
app.register_blueprint(pageBp, url_prefix="")
app.register_blueprint(attendanceBp, url_prefix="/api/attendance")
app.register_blueprint(employeesBp, url_prefix="/api/employees")
app.register_blueprint(branchRoutesBp, url_prefix="/api/branch")
app.register_blueprint(historyRoutesBp, url_prefix="/api/history")
app.register_blueprint(annualRequestBp, url_prefix="/api/annualRequest")



if __name__ == "__main__":
    app.run(debug=True)