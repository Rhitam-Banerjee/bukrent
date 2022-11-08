from flask import Blueprint, jsonify, request, render_template, redirect, session, url_for, make_response

from app.models.author import Author
from app.models.category import Category
from app.models.launch import Launch
from app.models.books import Book
from app.models.user import User, Address, Child, Preference
from app.models.series import Series
from app.models.order import Order
from app.models.buckets import *
from app.models.format import Format
from app.models.publishers import Publisher
from app.models.search import Search
from app import db

from functools import wraps

import os
from twilio.rest import Client
import jwt
import datetime

import razorpay

api = Blueprint('api', __name__, url_prefix="/api")

def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       access_token = request.cookies.get('access_token')
       if not access_token:
           return jsonify({'message': 'No access token'}), 401
       try:
           data = jwt.decode(access_token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
           user = User.query.filter_by(id=data['id']).first()
       except:
           return jsonify({'message': 'Invalid access token'})
       return f(user, *args, **kwargs)
   return decorator

@api.route("/submit-mobile", methods=["POST"])
def submit_mobile():
    mobile_number = request.json.get("mobile_number")
    if not mobile_number:
        return jsonify({
            "message": "Please enter your mobile number!",
            "status": "error"
        }), 400

    if len(mobile_number) != 10:
        return jsonify({
            "message": "Incorrect format for mobile number. Please make sure there are no spaces or country codes.",
            "status": "error"
        }), 400

    session["mobile_number"] = mobile_number
    user = User.query.filter_by(mobile_number=mobile_number).first()

    if user and user.password:
        return jsonify({
            "redirect": url_for('views.login'),
            "status": "success",
            "user": user.to_json(),
        }), 200
    elif user and user.payment_id:
        return jsonify({
            "redirect": url_for('views.confirm_mobile'),
            "status": "success",
            "message": "Already signed up. Our team will contact you through Whatsapp soon.",
            "user": user.to_json(),
        }), 200
    else:
        return jsonify({
            "redirect": url_for('views.signup'),
            "status": "success"
        }), 200

@api.route("/login", methods=["POST"])
def login():
    mobile_number = request.json.get('mobile_number')
    password = request.json.get("password")

    if not all((mobile_number, password)):
        return jsonify({
            "message": "Provide your credentials",
            "status": "error"
        }), 400

    user = User.query.filter_by(mobile_number=mobile_number).first()

    if user:
        if user.password == password:
            session["current_user"] = user.guid
            access_token = jwt.encode({'id' : user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=45)}, os.environ.get('SECRET_KEY'), "HS256")
            response = make_response(jsonify({
                "redirect": url_for("views.select_plan"),
                "status": "success",
                "user": user.to_json(),
            }), 200)
            response.set_cookie('access_token', access_token, secure=True, httponly=True, samesite='None')
            return response
            if not user.plan_id:
                return jsonify({
                    "redirect": url_for("views.select_plan"),
                    "status": "success",
                    "user": user.to_json(),
                }), 200
            if user.plan_id and not user.is_subscribed:
                return jsonify({
                    "redirect": url_for('views.selected_plan'),
                    "status": "success",
                    "user": user.to_json(),
                }), 200
            if len(user.address) == 0:
                return jsonify({
                    "redirect": url_for('views.add_address'),
                    "status": "success",
                    "user": user.to_json(),
                }), 200
            if len(user.child) == 0:
                return jsonify({
                    "redirect": url_for('views.add_children'),
                    "status": "success",
                    "user": user.to_json(),
                }), 200
            return jsonify({
                "redirect": url_for('views.preferences'),
                "status": "success",
                "user": user.to_json(),
            }), 200
        else:
            return jsonify({
                "message": "Incorrect Password!",
                "status": "error"
            }), 400
    else:
        return jsonify({
            "message": "No User with that mobile number exists!",
            "status": "error"
        }), 400

@api.route("/signup", methods=["POST"])
def signup():
    first_name = request.json.get("first_name")
    last_name = request.json.get("last_name")
    password = request.json.get("password")
    confirm_password = request.json.get("confirm_password")

    if not all((first_name, password, confirm_password)):
        return jsonify({
            "message": "Fill all the details!",
            "status": "error"
        }), 400

    if len(password) < 6:
        return jsonify({
            "message": "Password should be atleast 6 characters long",
            "status": "error"
        }), 400

    if password != confirm_password:
        return jsonify({
            "message": "Password and Confirm Password don't match",
            "status": "error"
        }), 400

    session["first_name"] = first_name
    session["last_name"] = last_name
    session["password"] = password

    mobile_number = session.get("mobile_number")

    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    verification = client.verify.services(os.environ.get('OTP_SERVICE_ID')).verifications.create(to=f"+91{mobile_number}", channel="sms")

    return jsonify({
        "redirect": url_for('views.confirm_mobile'),
        "status": "success"
    }), 201

@api.route("/resend-otp", methods=["POST"])
def resend_otp():
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    mobile_number = request.json.get('mobile_number')
    if not mobile_number:
        mobile_number = session.get('mobile_number')
        if not mobile_number:
            return jsonify({"message": "No mobile number", "status": "error"}), 400

    verification = client.verify.services(os.environ.get('OTP_SERVICE_ID')).verifications.create(to=f"+91{mobile_number}", channel="sms")

    return jsonify({
        "message": "OTP Sent!",
        "status": "success"
    }), 201

@api.route("/confirm-mobile", methods=["POST"])
def confirm_mobile():
    verification_code = request.json.get("otp")

    if not verification_code:
        return jsonify({
            "message": "Please enter the OTP",
            "status": "error"
        }), 400

    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    mobile_number = request.json.get('mobile_number')
    if not mobile_number:
        mobile_number = session.get('mobile_number')
        if not mobile_number:
            return jsonify({"message": "No mobile number", "status": "error"}), 400

    try:
        verification_check = client.verify.services(os.environ.get("OTP_SERVICE_ID")).verification_checks.create(to=f"+91{mobile_number}", code=verification_code)
        if verification_check.status == "approved":
            session["verified"] = True
            return jsonify({
                "status": "success",
            }), 201
        else:
            raise ValueError('Verification Failed! Try again.')
    except:
        return jsonify({
        "message": "Verification Failed! Try Again.",
        "status": "error"
        }), 400

@api.route("/add-details", methods=["POST"])
def add_details():
    email = request.json.get("email")
    password = request.json.get("password")
    confirm_password = request.json.get("confirm_password")

    if len(password) < 6:
        return jsonify({
            "message": "Password should be atleast 6 characters long",
            "status": "error"
        }), 400

    if password != confirm_password:
        return jsonify({
            "message": "Password and Confirm Password don't match",
            "status": "error"
        }), 400

    user = User.query.filter_by(guid=session.get("current_user")).first()

    user.update_details(email, password)

    return jsonify({
        "redirect": url_for('views.select_plan'),
        "status": "success"
    }), 201

@api.route("/choose-plan", methods=["POST"])
def choose_plan():
    plan = request.json.get("plan")
    mobile_number = request.json.get('mobile_number')
    if not mobile_number:
        mobile_number = session.get('mobile_number')
        if not mobile_number:
            return jsonify({"message": "No mobile number", "status": "error"}), 400
    user = User.query.filter_by(mobile_number=mobile_number).first()
    if not user:
        user = User.create('', '', mobile_number, '')
        db.session.add(user)
        db.session.commit()
    user.update_plan(plan)

    return jsonify({
        "redirect": url_for('views.selected_plan'),
        "status": "success"
    }), 201

@api.route("/change-plan", methods=["POST"])
def change_plan():
    mobile_number = request.json.get('mobile_number')
    if not mobile_number:
        mobile_number = session.get('mobile_number')
        if not mobile_number:
            return jsonify({"message": "No mobile number", "status": "error"}), 400
    user = User.query.filter_by(mobile_number=mobile_number).first()
    if not user:
        return jsonify({
            "message": "Session expired",
            "status": "error"
        }), 401

    user.remove_plan()

    return jsonify({
        "redirect": url_for('views.select_plan'),
        "status": "success"
    }), 201

@api.route("/choose-card", methods=["POST"])
def choose_card():
    card = request.json.get("card")
    if card == 1:
        return jsonify({
            "redirect": url_for('views.confirm_subscription'),
            "status": "success"
        }), 200
    else:
        return jsonify({
            "redirect": url_for('views.confirm_payment'),
            "status": "success"
        }), 200

@api.route("/generate-subscription-id", methods=["POST"])
def generate_subscription_id():
    mobile_number = request.json.get('mobile_number')
    if not mobile_number:
        mobile_number = session.get('mobile_number')
        if not mobile_number:
            return jsonify({"message": "No mobile number", "status": "error"}), 400
    user = User.query.filter_by(mobile_number=mobile_number).first()
    if not user:
        return jsonify({
            "message": "Session expired",
            "status": "error"
        }), 401

    client = razorpay.Client(auth=(os.environ.get("RZP_KEY_ID"), os.environ.get("RZP_KEY_SECRET")))

    if user.plan_id == os.environ.get("RZP_PLAN_1_ID"):
        plan_desc = "Get 1 Book Per Week"
    elif user.plan_id == os.environ.get("RZP_PLAN_2_ID"):
        plan_desc = "Get 2 Books Per Week"
    elif user.plan_id == os.environ.get("RZP_PLAN_3_ID"):
        plan_desc = "Get 4 Books Per Week"

    subscription = client.subscription.create({
        'plan_id': user.plan_id,
        'total_count': 36
    })

    subscription_id = subscription.get("id")

    user.add_subscription_details(subscription_id)

    return jsonify({
        "subscription_id": subscription_id,
        "key": os.environ.get("RZP_KEY_ID"),
        "name": f"{user.first_name}",
        "contact": f"+91{user.mobile_number}",
        "plan_desc": plan_desc
    }), 201

@api.route("/generate-order-id", methods=["POST"])
def generate_order_id():
    mobile_number = request.json.get('mobile_number')
    if not mobile_number:
        return jsonify({"message": "No mobile number" }), 400
    user = User.query.filter_by(mobile_number=mobile_number).first()
    client = razorpay.Client(auth=(os.environ.get("RZP_KEY_ID"), os.environ.get("RZP_KEY_SECRET")))

    card = request.json.get('card')
    if card not in [3, 12]:
        return jsonify({
            "message": "Invalid card",
            "status": "error"
        }), 400

    client = razorpay.Client(auth=(os.environ.get("RZP_KEY_ID"), os.environ.get("RZP_KEY_SECRET")))

    if user.plan_id == os.environ.get("RZP_PLAN_1_ID"):
        amount = 349 * card
        plan_desc = "Get 1 Book Per Week"
    elif user.plan_id == os.environ.get("RZP_PLAN_2_ID"):
        amount = 479 * card
        plan_desc = "Get 2 Books Per Week"
    elif user.plan_id == os.environ.get("RZP_PLAN_3_ID"):
        amount = 599 * card
        plan_desc = "Get 4 Books Per Week"

    if card == 12:
        amount = int(amount - 0.1 * amount)

    order = client.order.create({
        "amount": amount * 100,
        "currency": "INR"
    })

    order_id = order.get("id")

    user.add_order_details(order_id)

    return jsonify({
        "order_id": order_id,
        "key": os.environ.get("RZP_KEY_ID"),
        "name": f"{user.first_name}",
        "contact": f"+91{user.mobile_number}",
        "plan_desc": plan_desc
    }), 201

@api.route("/verify-subscription", methods=["POST"])
def verify_subscription():
    try:
        payment_id = request.json.get("payment_id")
        subscription_id = request.json.get("subscription_id")
        signature = request.json.get("signature")

        # client = razorpay.Client(auth=(os.environ.get("RZP_KEY_ID"), os.environ.get("RZP_KEY_SECRET")))

        # result = client.utility.verify_payment_signature({
        #     'razorpay_subscription_id': subscription_id,
        #     'razorpay_payment_id': payment_id,
        #     'razorpay_signature': signature
        # })

        return jsonify({
            "message": "Payment Successful!",
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "message": "Payment Failed! Please try again!",
            "status": "error"
        }), 400

@api.route("/verify-order", methods=["POST"])
def verify_order():
    try:
        payment_id = request.json.get("payment_id")
        order_id = request.json.get("order_id")
        signature = request.json.get("signature")

        client = razorpay.Client(auth=(os.environ.get("RZP_KEY_ID"), os.environ.get("RZP_KEY_SECRET")))

        result = client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })

        return jsonify({
            "message": "Payment Successful!",
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "message": "Payment Failed! Please try again!",
            "status": "error"
        }), 400

@api.route("/subscription-successful", methods=["POST"])
def subscription_successful():
    subscription_id = request.json.get("subscription_id")
    payment_id = request.json.get("payment_id")

    mobile_number = request.json.get('mobile_number')
    if not mobile_number:
        mobile_number = session.get('mobile_number')
        if not mobile_number:
            return jsonify({"message": "No mobile number", "status": "error"}), 400
    user = User.query.filter_by(mobile_number=mobile_number).first()
    if not user:
        return jsonify({
            "message": "Session expired",
            "status": "error"
        }), 401

    user.update_subscription_details(subscription_id, payment_id)

    return jsonify({
        "status": "success"
    }), 201

@api.route("/payment-successful", methods=["POST"])
def payment_successful():
    payment_id = request.json.get("payment_id")
    order_id = request.json.get("order_id")

    mobile_number = request.json.get('mobile_number')
    if not mobile_number:
        mobile_number = session.get('mobile_number')
        if not mobile_number:
            return jsonify({"message": "No mobile number", "status": "error"}), 400
    user = User.query.filter_by(mobile_number=mobile_number).first()
    if not user:
        return jsonify({
            "message": "Session expired",
            "status": "error"
        }), 401

    user.update_payment_details(order_id, payment_id)

    return jsonify({
        "status": "success"
    }), 201

@api.route("/add-address", methods=["POST"])
def add_address():
    try:
        address_json = dict(
            house_number = request.json.get("house_number"),
            building = request.json.get("building"),
            area = request.json.get("area"),
            landmark = request.json.get("landmark"),
            pin_code = request.json.get("pin_code")
        )

        user = User.query.filter_by(guid=session.get("current_user")).first()

        Address.create(address_json, user.id)

        return jsonify({
            "redirect": url_for('views.add_children'),
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "success"
        }), 400

@api.route("/add-children", methods=["POST"])
def add_children():
    try:
        children = request.json.get("children")

        for child in children:
            if not all((child.get("name"), child.get("dob"), child.get("age_group"))):
                return jsonify({
                    "message": "All fields for all the kids are necessary.",
                    "status": "error"
                }), 400

        user = User.query.filter_by(guid=session.get("current_user")).first()

        for child in children:
            user.add_child(child)

        age_groups = []
        for child in children:
            age_groups.append(child.get("age_group"))

        age_groups = list(set(age_groups))

        user.add_age_groups(age_groups)

        return jsonify({
            "status": "success",
            "guid": user.child[0].guid
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/submit-preferences", methods=["POST"])
@token_required
def submit_preferences(user):
    try:
        guid = request.json.get("guid")
        preference_data = request.json.get("preference_data")
        if not guid:
            return jsonify({
                "message": "Bad request. No child identified",
                "status": "success"
            }), 400
        child = Child.query.filter_by(guid=guid).first()
        if child.preferences:
            child.preferences.update(preference_data)
        else:
            Preference.create(
                preference_data.get("last_book_read1"),
                preference_data.get("last_book_read2"),
                preference_data.get("last_book_read3"),
                preference_data.get("books_read_per_week"),
                preference_data.get('reading_level'),
                preference_data.get("categories"),
                preference_data.get("formats"),
                preference_data.get("authors"),
                preference_data.get("series"),
                child.id
            )

        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()
        for child_obj in user.child:
            if not child_obj.preferences:
                return jsonify({
                    "redirect": f"{url_for('views.preferences')}?guid={child_obj.guid}"
                }), 201
        return jsonify({
            "redirect": url_for('views.library')
        }), 201
    except Exception as e:
        print(e)
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route('/get-user')
@token_required
def get_user(user):
    try:
        if not user:
            user = User.query.filter_by(guid=session['current_user']).first()
        if not user:
            return jsonify({
                "message": "No user session",
                "status": "error"
            }), 400
        return jsonify({
            "user": user.to_json(),
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/get-user-data")
def get_user_guid():
    try:
        mobile_number = request.args.get("mobile")

        if not mobile_number:
            return jsonify({
                "message": "Mobile number is required!",
                "status": "error"
            }), 400

        user = User.query.filter_by(mobile_number=mobile_number).first()

        if not user:
            return jsonify({
                "message": "No user with the given mobile number found.",
                "status": "error"
            }), 400

        return jsonify({
            "data": user.to_json(),
            "status": "success"
        }), 200

    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/get-wishlists")
@token_required
def get_wishlists(user):
    try:
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()
        if not user:
            guid = request.args.get("guid")
            user = User.query.filter_by(guid=guid).first()
            if not user:
                return jsonify({
                    "message": "User Not Found",
                    "status": "error"
                }), 400

        return jsonify({
            "status": "success",
            "wishlists": user.get_wishlist()
        }), 200

    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/get-suggestions")
@token_required
def get_suggestions(user):
    try:
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()
        if not user:
            guid = request.args.get("guid")
            user = User.query.filter_by(guid=guid).first()
            if not user:
                return jsonify({
                    "message": "User Not Found",
                    "status": "error"
                }), 400
        return jsonify({
            "status": "success",
            "suggestions": user.get_suggestions()
        }), 200

    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/get-dumps")
@token_required
def get_dumps(user):
    try:
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()
        if not user:
            guid = request.args.get("guid")
            user = User.query.filter_by(guid=guid).first()
            if not user:
                return jsonify({
                    "message": "User Not Found",
                    "status": "error"
                }), 400

        return jsonify({
            "status": "success",
            "dumps": user.get_dump_data()
        }), 200

    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route('/get-previous-books')
@token_required
def get_previous_books(user):
    try:
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()
        return jsonify({
            "status": "success",
            "books": user.get_previous_books()
        }), 200
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route('/get-current-books')
@token_required
def get_current_books(user):
    try:
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()
        if not user:
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 200
        return jsonify({
            "status": "success",
            "books": user.get_current_books()
        }), 200
    except Exception as e:
        print(e)
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/get-buckets")
@token_required
def get_buckets(user):
    try:
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()
        if not user:
            guid = request.args.get("guid")
            user = User.query.filter_by(guid=guid).first()
            if not user:
                return jsonify({
                    "message": "User Not Found",
                    "status": "error"
                }), 400

        return jsonify({
            "status": "success",
            "wishlists": user.get_next_bucket()
        }), 200

    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/get-previous-bucket")
def get_previous_bucket():
    try:
        user = User.query.filter_by(guid=session.get("current_user")).first()
        if not user:
            guid = request.args.get("guid")
            user = User.query.filter_by(guid=guid).first()
            if not user:
                return jsonify({
                    "message": "User Not Found",
                    "status": "error"
                }), 400

        return jsonify({
            "status": "success",
            "wishlists": user.get_previous_bucket()
        }), 200

    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/add-to-wishlist", methods=["POST"])
@token_required
def add_to_wishlist(user):
    try:
        guid = request.json.get("guid")
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()
        if not user:
            user_guid = request.json.get("user_guid")
            user = User.query.filter_by(guid=user_guid).first()
            if not user:
                return jsonify({
                    "message": "User Not Found",
                    "status": "error"
                }), 400

        user.add_to_wishlist(guid)

        return jsonify({
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/suggestion-to-wishlist", methods=["POST"])
@token_required
def suggestion_to_wishlist(user):
    try:
        guid = request.json.get("guid")
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()

        if not user:
            user_guid = request.json.get("user_guid")
            user = User.query.filter_by(guid=user_guid).first()
            if not user:
                return jsonify({
                    "message": "User Not Found",
                    "status": "error"
                }), 400

        user.suggestion_to_wishlist(guid)

        suggestions = user.get_suggestions()
        wishlists = user.get_wishlist()

        return jsonify({
            "status": "success",
            "suggestions": suggestions,
            "wishlists": wishlists
        }), 201

    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/suggestion-to-dump", methods=["POST"])
@token_required
def suggestion_to_dump(user):
    try:
        guid = request.json.get("guid")
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()

        if not user:
            user_guid = request.json.get("user_guid")
            user = User.query.filter_by(guid=user_guid).first()
            if not user:
                return jsonify({
                    "message": "User Not Found",
                    "status": "error"
                }), 400

        user.suggestion_to_dump(guid)

        suggestions = user.get_suggestions()
        dumps = user.get_dump_data()

        return jsonify({
            "status": "success",
            "suggestions": suggestions,
            "dumps": dumps
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/dump-action-read", methods=["POST"])
@token_required
def dump_action_read(user):
    try:
        guid = request.json.get("guid")
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()

        if not user:
            user_guid = request.json.get("user_guid")
            user = User.query.filter_by(guid=user_guid).first()
            if not user:
                return jsonify({
                    "message": "User Not Found",
                    "status": "error"
                }), 400

        user.dump_action_read(guid)

        dumps = user.get_dump_data()
        read_books = user.get_read_books()

        return jsonify({
            "status": "success",
            "dumps": dumps,
            "read_books": read_books
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/dump-action-dislike", methods=["POST"])
@token_required
def dump_action_dislike(user):
    try:
        guid = request.json.get("guid")
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()

        if not user:
            user_guid = request.json.get("user_guid")
            user = User.query.filter_by(guid=user_guid).first()
            if not user:
                return jsonify({
                    "message": "User Not Found",
                    "status": "error"
                }), 400

        user.dump_action_dislike(guid)

        dumps = user.get_dump_data()

        return jsonify({
            "status": "success",
            "dumps": dumps
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/wishlist-next", methods=["POST"])
@token_required
def wishlist_next(user):
    try:
        guid = request.json.get("guid")
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()

        if not user:
            user_guid = request.json.get("user_guid")
            user = User.query.filter_by(guid=user_guid).first()
            if not user:
                return jsonify({
                    "message": "User Not Found",
                    "status": "error"
                }), 400

        user.wishlist_next(guid)

        wishlists = user.get_wishlist()

        return jsonify({
            "status": "success",
            "wishlists": wishlists
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/wishlist-prev", methods=["POST"])
@token_required
def wishlist_prev(user):
    try:
        guid = request.json.get("guid")
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()

        if not user:
            user_guid = request.json.get("user_guid")
            user = User.query.filter_by(guid=user_guid).first()
            if not user:
                return jsonify({
                    "message": "User Not Found",
                    "status": "error"
                }), 400

        user.wishlist_prev(guid)

        wishlists = user.get_wishlist()

        return jsonify({
            "status": "success",
            "wishlists": wishlists
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/wishlist-remove", methods=["POST"])
@token_required
def wishlist_remove(user):
    try:
        guid = request.json.get("guid")
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()

        if not user:
            user_guid = request.json.get("user_guid")
            user = User.query.filter_by(guid=user_guid).first()
            if not user:
                return jsonify({
                    "message": "User Not Found",
                    "status": "error"
                }), 400

        user.wishlist_remove(guid)

        wishlists = user.get_wishlist()
        dumps = user.get_dump_data()

        return jsonify({
            "status": "success",
            "wishlists": wishlists,
            "dumps": dumps
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/create-bucket-list")
@token_required
def create_bucket_list(user):
    try:
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()
        if not user:
            return jsonify({
                "message": "Unauthorized",
                "status": "error"
            }), 400

        user.create_bucket_list()
        return jsonify({
            "message": "Buckets Created!",
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/bucket-remove", methods=["POST"])
@token_required
def bucket_remove(user):
    try:
        guid = request.json.get("guid")
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()

        if not user:
            user_guid = request.json.get("user_guid")
            user = User.query.filter_by(guid=user_guid).first()
            if not user:
                return jsonify({
                    "message": "User Not Found",
                    "status": "error"
                }), 400

        user.bucket_remove(guid)
        return jsonify({
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/change-delivery-date", methods=["POST"])
@token_required
def change_delivery_date(user):
    try:
        delivery_date = request.json.get("delivery_date")
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()

        if not user:
            user_guid = request.json.get("user_guid")
            user = User.query.filter_by(guid=user_guid).first()
            if not user:
                return jsonify({
                    "message": "User Not Found",
                    "status": "error"
                }), 400

        user.change_delivery_date(delivery_date)
        return jsonify({
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/confirm-order")
@token_required
def confirm_order(user):
    try:
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()

        if not user:
            return jsonify({
                "message": "No user found.",
                "status": "error"
            }), 400

        user.confirm_order()
        return jsonify({
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/retain-book", methods=["POST"])
@token_required
def retain_book(user):
    try:
        guid = request.json.get("guid")
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()

        if not user:
            user_guid = request.json.get("user_guid")
            user = User.query.filter_by(guid=user_guid).first()
            if not user:
                return jsonify({
                    "message": "User Not Found",
                    "status": "error"
                }), 400

        user.retain_book(guid)
        return jsonify({
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/retain-current-book", methods=["POST"])
@token_required
def retain_current_book(user):
    try:
        guid = request.json.get("guid")
        if not user:
            user = User.query.filter_by(guid=session.get("current_user")).first()

        if not user:
            user_guid = request.json.get("user_guid")
            user = User.query.filter_by(guid=user_guid).first()
            if not user:
                return jsonify({
                    "message": "User Not Found",
                    "status": "error"
                }), 400

        user.retain_current_book(guid)
        return jsonify({
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/logout", methods=["POST"])
@token_required
def logout(user):
    response = make_response(jsonify({
        "message": "Success!",
        "status": "success"
    }), 201)
    session["current_user"] = None
    response.set_cookie('access_token', '', secure=True, httponly=True, samesite='None')
    return response

# @api.route("/cart-checkout", methods=["POST"])
# def cart_checkout():
#     session["cart_checkout"] = True

#     current_user = session.get("current_user")
#     user = User.query.filter_by(guid=current_user).first()

#     if current_user:
#         if user.is_subscribed:
#             return jsonify({
#                 "redirect": url_for('views.add_address'),
#                 "status": "success"
#             }), 201
#         else:
#             if session.get("plan"):
#                 return jsonify({
#                     "redirect": url_for('views.confirm_plan'),
#                     "status": "success"
#                 }), 201
#             else:
#                 return jsonify({
#                     "redirect": url_for('views.become_a_subscriber'),
#                     "status": "success"
#                 }), 201
#     else:
#         return jsonify({
#             "redirect": url_for('views.signup'),
#             "status": "success"
#         }), 201

# @api.route("/add-to-cart", methods=["POST"])
# def add_to_cart():
#     try:
#         book_guid = request.json.get("guid")
#         book = Book.query.filter_by(guid=book_guid).first()
#         current_user_guid = session.get("current_user")
#         if current_user_guid:
#             current_user = User.query.filter_by(guid=session.get("current_user")).first()
#             cart = Cart.query.filter_by(user_id=current_user.id).first()
#             cart.add_book(book)
#         else:
#             if session.get("cart"):
#                 cart = session.get("cart")
#                 cart.append(book.guid)
#                 session["cart"] = cart
#             else:
#                 session["cart"] = [book.guid]

#         return jsonify({
#             "message": "Added",
#             "status": "success"
#         }), 201
#     except Exception as e:
#         return jsonify({
#             "message": str(e),
#             "status": "error"
#         }), 400

# @api.route("/add-to-wishlist", methods=["POST"])
# def add_to_wishlist():
#     try:
#         book_guid = request.json.get("guid")
#         book = Book.query.filter_by(guid=book_guid).first()
#         current_user_guid = session.get("current_user")
#         if current_user_guid:
#             current_user = User.query.filter_by(guid=session.get("current_user")).first()
#             wishlist = Wishlist.query.filter_by(user_id=current_user.id).first()
#             wishlist.add_book(book)
#         else:
#             if session.get("wishlist"):
#                 wishlist = session.get("wishlist")
#                 wishlist.append(book.guid)
#                 session["wishlist"] = wishlist
#             else:
#                 session["wishlist"] = [book.guid]

#         return jsonify({
#             "message": "Added",
#             "status": "success"
#         }), 201
#     except Exception as e:
#         return jsonify({
#             "message": str(e),
#             "status": "error"
#         }), 400

# @api.route("/move-to-wishlist", methods=["POST"])
# def move_to_wishlist():
#     try:
#         book_guid = request.json.get('guid')
#         book = Book.query.filter_by(guid=book_guid).first()
#         current_user_guid = session.get("current_user")
#         if current_user_guid:
#             current_user = User.query.filter_by(guid=current_user_guid).first()
#             current_user.move_book_to_wishlist(book)
#         else:
#             cart = session.get("cart")
#             cart.remove(book_guid)
#             session["cart"] = cart
#             if session.get("wishlist"):
#                 wishlist = session.get("wishlist")
#                 wishlist.append(book_guid)
#                 session["wishlist"] = wishlist
#             else:
#                 session["wishlist"] = [book_guid]
#         return jsonify({
#             "message": "Moved",
#             "status": "success"
#         }), 201
#     except Exception as e:
#         return jsonify({
#             "message": str(e),
#             "status": "error"
#         }), 400

# @api.route("/move-to-cart", methods=["POST"])
# def move_to_cart():
#     try:
#         book_guid = request.json.get('guid')
#         book = Book.query.filter_by(guid=book_guid).first()
#         current_user_guid = session.get("current_user")
#         if current_user_guid:
#             current_user = User.query.filter_by(guid=current_user_guid).first()
#             current_user.move_book_to_cart(book)
#         else:
#             wishlist = session.get("wishlist")
#             wishlist.remove(book_guid)
#             session["wishlist"] = wishlist
#             if session.get("cart"):
#                 cart = session.get("cart")
#                 cart.append(book_guid)
#                 session["cart"] = cart
#             else:
#                 session["cart"] = [book_guid]
#         return jsonify({
#             "message": "Moved",
#             "status": "success"
#         }), 201
#     except Exception as e:
#         return jsonify({
#             "message": str(e),
#             "status": "error"
#         }), 400

# @api.route("/delete-from-cart", methods=["POST"])
# def delete_from_cart():
#     try:
#         book_guid = request.json.get('guid')
#         book = Book.query.filter_by(guid=book_guid).first()
#         current_user_guid = session.get("current_user")
#         if current_user_guid:
#             current_user = User.query.filter_by(guid=current_user_guid).first()
#             current_user.remove_book_from_cart(book)
#         else:
#             cart = session.get("cart")
#             cart.remove(book_guid)
#             session["cart"] = cart
#         return jsonify({
#             "message": "Moved",
#             "status": "success"
#         }), 201
#     except Exception as e:
#         return jsonify({
#             "message": str(e),
#             "status": "error"
#         }), 400

# @api.route("/delete-from-wishlist", methods=["POST"])
# def delete_from_wishlist():
#     try:
#         book_guid = request.json.get('guid')
#         book = Book.query.filter_by(guid=book_guid).first()
#         current_user_guid = session.get("current_user")
#         if current_user_guid:
#             current_user = User.query.filter_by(guid=current_user_guid).first()
#             current_user.remove_book_from_wishlist(book)
#         else:
#             wishlist = session.get("wishlist")
#             wishlist.remove(book_guid)
#             session["wishlist"] = wishlist
#         return jsonify({
#             "message": "Moved",
#             "status": "success"
#         }), 201
#     except Exception as e:
#         return jsonify({
#             "message": str(e),
#             "status": "error"
#         }), 400

# @api.route("/check-books", methods=["POST"])
# def check_books():
#     current_user = session.get("current_user")
#     user = User.query.filter_by(guid=current_user).first()
#     if len(user.cart.books) < user.books_per_week:
#         return jsonify({
#             "message": f"You should have at least {user.books_per_week} books in your cart to place an order.",
#             "status": "error"
#         }), 400
#     else:
#         return jsonify({
#             "status": "success"
#         }), 200

# @api.route("/place-order", methods=["POST"])
# def place_order():
#     try:
#         current_user = session.get("current_user")
#         user = User.query.filter_by(guid=current_user).first()

#         if user.books_per_week != len(request.json.get("books")):
#             return jsonify({
#                 "message": f"Select {user.books_per_week} books to place an order.",
#                 "status": "error"
#             }), 400

#         billing_address = Address.create(request.json.get("billing_address"), user.id)
#         if request.json.get("same_as_billing"):
#             delivery_address = billing_address
#         else:
#             delivery_address = Address.create(request.json.get("delivery_address"), user.id)

#         is_gift = request.json.get("is_gift")
#         gift_message = request.json.get("gift_message")
#         books = request.json.get("books")

#         Order.create(user.id, billing_address.id, delivery_address.id, is_gift, gift_message, books)
#         for book in books:
#             user.remove_book_from_cart(Book.query.filter_by(guid=book).first())

#         return jsonify({
#             "message": "Order Placed",
#             "status": "success"
#         }), 201
#     except Exception as e:
#         return jsonify({
#             "message": str(e),
#             "status": "error"
#         }), 400

# @api.route("/get-amazon-bestsellers", methods=["POST"])
# def get_amazon_bestsellers():
#     age_group = request.json.get("age_group")
#     return jsonify({
#         "data": Book.get_amazon_bestsellers(age_group),
#         "status": "success"
#     }), 200

@api.route("/get-most-borrowed")
def get_most_borrowed():
    try:
        age_group = int(request.args.get("age"))
        start = int(request.args.get("start"))
        end = int(request.args.get("end"))

        books = Book.get_most_borrowed(age_group, start, end)

        return jsonify({
            "data": books,
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/get-bestsellers")
def get_bestsellers():
    try:
        age_group = int(request.args.get("age"))
        start = int(request.args.get("start"))
        end = int(request.args.get("end"))

        books = Book.get_bestsellers(age_group, start, end)

        return jsonify({
            "data": books,
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/get-authors")
def get_authors():
    try:
        age_group = int(request.args.get("age"))
        start = int(request.args.get("start"))
        end = int(request.args.get("end"))

        authors = Author.get_authors(age_group, start, end)

        return jsonify({
            "data": authors,
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/get-author-books")
def get_author_books():
    try:
        guid = request.args.get("guid")
        start = int(request.args.get("start"))
        end = int(request.args.get("end"))

        books = Book.get_author_books(guid, start, end)

        return jsonify({
            "data": books,
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/get-series")
def get_series():
    try:
        age_group = int(request.args.get("age"))
        start = int(request.args.get("start"))
        end = int(request.args.get("end"))

        series = Series.get_series(age_group, start, end)

        return jsonify({
            "data": series,
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/get-series-books")
def get_series_books():
    try:
        guid = request.args.get("guid")
        start = int(request.args.get("start"))
        end = int(request.args.get("end"))

        books = Book.get_series_books(guid, start, end)

        return jsonify({
            "data": books,
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/get-publishers")
def get_publishers():
    try:
        age_group = int(request.args.get("age"))
        start = int(request.args.get("start"))
        end = int(request.args.get("end"))

        publishers = Publisher.get_publishers(age_group, start, end)

        return jsonify({
            "data": publishers,
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/get-publisher-books")
def get_publisher_books():
    try:
        guid = request.args.get("guid")
        start = int(request.args.get("start"))
        end = int(request.args.get("end"))

        books = Book.get_publisher_books(guid, start, end)

        return jsonify({
            "data": books,
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/get-types")
def get_types():
    try:
        age_group = int(request.args.get("age"))
        start = int(request.args.get("start"))
        end = int(request.args.get("end"))

        types = Format.get_types(age_group, start, end)

        return jsonify({
            "data": types,
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/get-type-books")
def get_type_books():
    try:
        guid = request.args.get("guid")
        start = int(request.args.get("start"))
        end = int(request.args.get("end"))

        books = Book.get_type_books(guid, start, end)

        return jsonify({
            "data": books,
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/get-genres")
def get_genres():
    age_group = request.args.get("age")
    return jsonify({
        "data": Category.get_genres(age_group),
        "status": "success"
    }), 200

@api.route("/get-genres-books", methods=["POST"])
def get_genres_books():
    guid = request.json.get("guid")
    return jsonify({
        "data": Book.get_genres_books(guid),
        "name": Category.query.filter_by(guid=guid).first().name,
        "status": "success"
    }), 200

@api.route("/get-similar-books", methods=["POST"])
def get_similar_books():
    age_group = request.json.get("age_group")
    return jsonify({
        "data": Book.get_similar_books(age_group),
        "status": "success"
    }), 200

@api.route("/submit-search-form", methods=["POST"])
def submit_search_form():
    try:
        name = request.json.get("name")
        mobile_number = request.json.get("mobile_number")
        book_name = request.json.get("book_name")
        book_link = request.json.get("book_link")

        if not all((name, mobile_number, book_name, book_link)):
            return jsonify({
                "message": "All fields are mandatory!",
                "status": "error"
            }), 400

        Search.create(name, mobile_number, book_name, book_link)

        return jsonify({
            "message": "Submitted",
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/search")
def search():
    try:
        query = request.args.get("query")

        all_books = Book.query.filter(Book.name.ilike(f"%{query}%")).all()

        authors = Author.query.filter(Author.name.ilike(f"%{query}%")).all()
        series = Series.query.filter(Series.name.ilike(f"%{query}%")).all()
        publishers = Publisher.query.filter(Publisher.name.ilike(f"%{query}%")).all()

        return jsonify({
            "books": [book.to_json() for book in all_books],
            "authors": {
                "names": [author.name for author in authors],
                "books": [[book.to_json() for book in author.books] for author in authors]
            },
            "series": {
                "names": [serie.name for serie in series],
                "books": [[book.to_json() for book in serie.books] for serie in series]
            },
            "publishers": {
                "names": [publisher.name for publisher in publishers],
                "books": [[book.to_json() for book in publisher.books] for publisher in publishers]
            },
            "status": "success"
        }), 200

    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/get-book-details")
def get_book_details():
    try:
        guid = request.args.get("guid")
        if not guid:
            return jsonify({
                "message": "Book GUID is required!",
                "status": "error"
            }), 400

        book = Book.query.filter_by(guid=guid).first()

        if not book:
            return jsonify({
                "message": "No book with given GUID found!",
                "status": "error"
            }), 400

        return jsonify({
            "book": book.to_json(),
            "details": book.details.to_json(),
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "message": str(e),
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
