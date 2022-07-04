from flask import Blueprint, jsonify, request, render_template, redirect, session, url_for

from app.models.launch import Launch

api = Blueprint('api', __name__, url_prefix="/api")

@api.route("/signup")
def signup():
    first_name = request.json.get("first_name")
    last_name = request.json.get("last_name")
    mobile_number = request.json.get("mobile_number")
    newsletter = request.json.get("newsletter")

    if not all((first_name, last_name, mobile_number)):
        return jsonify({
            "message": "First Name, Last Name and Mobile Number are mandatory fields!",
            "status": "error"
        }), 400
    
    if len(mobile_number) != 10:
        return jsonify({
            "message": "Incorrect format for mobile number. Please make sure there are no spaces or country codes.",
            "status": "error"
        }), 400

@api.route("/launch", methods=["POST"])
def launch():
    parent_name = request.json.get("parent_name")
    mobile_number = request.json.get("mobile_number")
    child_name = request.json.get("child_name")
    age_group = request.json.get("age_group")

    if not all((parent_name, child_name, mobile_number, age_group)):
        return jsonify({
            "message": "All fields are mandatory!",
            "status": "error"
        }), 400
    
    Launch.create(parent_name, mobile_number, child_name, age_group)

    return jsonify({
        "message": "Saved!",
        "status": "success"
    }), 201