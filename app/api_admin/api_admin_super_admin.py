from app.api_admin.utils import api_admin, token_required
from flask import jsonify, request
from app.models.admin import Admin
from app.models.user import User
from app import db
from app.models.deliverer import Deliverer


def return_function(status, message):
    response_data = {"status": status, "message": message}
    status_code = 200
    if status == 'failure':
        status_code = 400
    return jsonify(response_data), status_code


@api_admin.route('/super-admin', methods=['POST'])
@token_required
def super_admin(admin):
    new = request.json['new']
    if new:
        username = request.json['username']
        password = request.json['password']
        database = request.json['database']
        if database == "admins":
            Admin.create(username=username, password=password, is_super_admin=1)
        elif database == "users":
            User.create("", "", mobile_number=username, password=password)
        else:
            Deliverer.create("", "", username=username, password=password, mobile_number="")
        db.session.commit()
        return return_function("success", f"{username} created in database {database}")
    database = request.json['database']
    username = request.json['fromUsername']
    change_username = request.json['toUsername']
    change_password = request.json['toPassword']
    failure, success = "failure", "success"

    if not change_username:
        return return_function(failure, "Please enter a new username value")

    if database == "admins":
        record = Admin.query.filter_by(username=username).first()
    elif database == "users":
        record = User.query.filter_by(mobile_number=username).first()
    else:
        record = Deliverer.query.filter_by(username=username).first()

    if not record:
        return return_function(failure, f"{database.capitalize()[:-1]} with username {username} not found.")

    if database == "users":
        record.mobile_number = change_username
    else:
        record.username = change_username

    if change_password:
        record.password = change_password

    db.session.commit()
    return return_function("success", "Changed Values Successfully.")


