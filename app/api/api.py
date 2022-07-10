from flask import Blueprint, jsonify, request, render_template, redirect, session, url_for

from app.models.launch import Launch
from app.models.user import User

import os
from twilio.rest import Client

import razorpay

api = Blueprint('api', __name__, url_prefix="/api")

@api.route("/signup", methods=["POST"])
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

    session["first_name"] = first_name
    session["last_name"] = last_name
    session["mobile_number"] = mobile_number
    session["newsletter"] = newsletter

    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    verification = client.verify.services(os.environ.get('OTP_SERVICE_ID')).verifications.create(to=f"+91{mobile_number}", channel="sms")

    return jsonify({
        "message": "OTP Sent!",
        "status": "success"
    }), 201

@api.route("/confirm-mobile", methods=["POST"])
def confirm_mobile():
    verification_code = request.json.get("verification_code")

    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    verification_check = client.verify.services(os.environ.get("OTP_SERVICE_ID")).verification_checks.create(to=f"+91{session.get('mobile_number')}", code=verification_code)

    if verification_check.status == "approved":
        User.create(session.get("first_name"), session.get("last_name"), session.get("mobile_number"), session.get("newsletter"))
        user = User.query.filter_by(mobile_number=session.get("mobile_number")).first()

        session["first_name"] = None
        session["last_name"] = None
        session["newsletter"] = None
        session["mobile_number"] = None

        session["current_user"] = user.guid

        return jsonify({
            "message": "Signup Successful!",
            "status": "error"
        }), 201
    else:
        return jsonify({
            "message": "Verification Failed! Try Again.",
            "status": "error"
        }), 400

@api.route("/generate-subscription-id", methods=["POST"])
def generate_subscription_id():
    plan = session.get("plan")
    if not plan:
        return jsonify({
            "message": "No Plan Selected!",
            "status": "error"
        }), 400
    
    client = razorpay.Client(auth=(os.environ.get("RZP_KEY_ID"), os.environ.get("RZP_KEY_SECRET")))

    if plan == "1":
        plan_id = os.environ.get("RZP_PLAN_1_ID")
        plan_desc = "Get 1 Book Per Week"
    elif plan == "2":
        plan_id = os.environ.get("RZP_PLAN_2_ID")
        plan_desc = "Get 2 Books Per Week"
    elif plan == "3":
        plan_id = os.environ.get("RZP_PLAN_3_ID")
        plan_desc = "Get 4 Books Per Week"
    else:
        plan_id = os.environ.get("RZP_PLAN_4_ID")
        plan_desc = "Get 6 Books Per Week"

    subscription = client.subscription.create({
        'plan_id': plan_id,
        'total_count': 36,
        'addons': [
            {
                "item": {
                    "name": "Security deposit",
                    "amount": 50000,
                    "currency": "INR"
                }
            }
        ]
    })

    subscription_id = subscription.get("id")
    plan_id = subscription.get("plan_id")

    current_user = User.query.filter_by(guid=session.get('current_user')).first()
    current_user.add_subscription_details(plan, plan_id, subscription_id)

    return jsonify({
        "subscription_id": subscription_id,
        "key": os.environ.get("RZP_KEY_ID"),
        "name": f"{current_user.first_name} {current_user.last_name}",
        "contact": f"+91{current_user.mobile_number}",
        "plan_desc": plan_desc
    }), 201

@api.route("/payment-successful", methods=["POST"])
def payment_successful():
    current_user = User.query.filter_by(guid=session.get('current_user')).first()
    client = razorpay.Client(auth=(os.environ.get("RZP_KEY_ID"), os.environ.get("RZP_KEY_SECRET")))
    subscription = client.subscription.fetch(current_user.subscription_id)

    current_user.add_customer_id(subscription.get("customer_id"))

    return redirect(url_for("views.payment_successful"))

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