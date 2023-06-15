from flask import jsonify, request, url_for, make_response

from app.models.author import Author
from app.models.category import Category
from app.models.books import Book
from app.models.user import User, Address, Child, Preference
from app.models.series import Series
from app.models.buckets import *
from app.models.format import Format
from app.models.publishers import Publisher
from app.models.search import Search
from app import db

from app.api_v2.utils import api_v2, token_required

import os
from twilio.rest import Client
import jwt

import razorpay

@api_v2.route("/submit-mobile", methods=["POST"])
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

    user = User.query.filter_by(mobile_number=mobile_number).first()

    if user: 
        if user.is_deleted: 
            return jsonify({
                "message": "Account with given mobile number was archived",
                "status": "error"
            }), 400
        if user.password and user.payment_status == 'Paid' and user.first_name and len(user.address) and len(user.child):
            return jsonify({
                "redirect": url_for('views.login'),
                "status": "success",
                "user": user.to_json(),
            }), 200
    if not user: 
        User.create('', '', mobile_number, '')
        user = User.query.filter_by(mobile_number=mobile_number).first()

    # account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    # auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    # client = Client(account_sid, auth_token)

    # verification = client.verify.services(os.environ.get('OTP_SERVICE_ID')).verifications.create(to=f"+91{mobile_number}", channel="sms")

    if user:
        return jsonify({
            "redirect": url_for('views.confirm_mobile'),
            "status": "success",
            "user": user.to_json(),
        }), 200
    else:
        return jsonify({
            "redirect": url_for('views.signup'),
            "status": "success"
        }), 200

@api_v2.route("/login", methods=["POST"])
def login():
    mobile_number = request.json.get('mobile_number')
    password = request.json.get("password")

    if not all((mobile_number, password)):
        return jsonify({
            "message": "Password not entered!",
            "status": "error"
        }), 400

    user = User.query.filter_by(mobile_number=mobile_number).first()

    if user: 
        if user.is_deleted: 
            return jsonify({
                "message": "Account with given mobile number was archived",
                "status": "error"
            }), 400
        if user.password == password:
            access_token = jwt.encode({'id' : user.id}, os.environ.get('SECRET_KEY'), "HS256")
            response = None
            if not user.plan_id:
                response = make_response(jsonify({
                    "redirect": url_for("views.select_plan"),
                    "status": "success",
                    "user": user.to_json(),
                }), 200)
            if user.plan_id and not user.is_subscribed:
                response = make_response(jsonify({
                    "redirect": url_for('views.selected_plan'),
                    "status": "success",
                    "user": user.to_json(),
                }), 200)
            if len(user.address) == 0:
                response = make_response(jsonify({
                    "redirect": url_for('views.add_address'),
                    "status": "success",
                    "user": user.to_json(),
                }), 200)
            if len(user.child) == 0:
                response = make_response(jsonify({
                    "redirect": url_for('views.add_children'),
                    "status": "success",
                    "user": user.to_json(),
                }), 200)
            else:
                response = make_response(jsonify({
                    "redirect": url_for('views.preferences'),
                    "status": "success",
                    "user": user.to_json(),
                }), 200)
            response.set_cookie('access_token', access_token, secure=True, httponly=True, samesite='None')
            return response
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

@api_v2.route("/signup", methods=["POST"])
def signup():
    mobile_number = request.json.get('mobile_number')
    name = request.json.get('name')
    children = request.json.get("children")
    address = request.json.get('address')
    pin_code = request.json.get('pin_code')
    contact_number = request.json.get('contact_number')

    if not all((name, address, pin_code, contact_number, mobile_number, children)):
        return jsonify({
            "message": "Fill all the details!",
            "status": "error"
        }), 400
    if not len(children):
        return jsonify({
            "message": "Add atleast 1 child",
            "status": "error"
        }), 400
    for child in children:
        if not all((child.get("name"), child.get("dob"), child.get("age_group"))):
            return jsonify({
                "message": "All fields for all the kids are necessary.",
                "status": "error"
            }), 400

    user = User.query.filter_by(mobile_number=mobile_number).first()
    if not user:
        return jsonify({
            "message": "Invalid mobile number",
            "status": "error"
        }), 400
    elif not user.payment_id or user.payment_status != 'Paid':
        return jsonify({
            "message": "Payment not done",
            "status": "error"
        }), 401

    try:
        user.first_name = name.split()[0]
        if len(name.split()) > 1:
            user.last_name = ''.join(name.split()[1:])
        user.password = '12345'
        user.contact_number = contact_number
        user.is_deleted = False

        Address.create({"area": address, "pin_code": pin_code}, user.id)

        for child in children:
            user.add_child(child)

        db.session.commit()

        access_token = jwt.encode({'id' : user.id}, os.environ.get('SECRET_KEY'), "HS256")

        response = make_response(jsonify({
            "redirect": url_for('views.confirm_mobile'),
            "status": "success"
        }), 201)
        response.set_cookie('access_token', access_token, secure=True, httponly=True, samesite='None')

        return response
    except Exception as e:
        print(e)
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api_v2.route("/resend-otp", methods=["POST"])
def resend_otp():
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    mobile_number = request.json.get('mobile_number')

    try:
        verification = client.verify.services(os.environ.get('OTP_SERVICE_ID')).verifications.create(to=f"+91{mobile_number}", channel="sms")
    except:
        return jsonify({
            "message": "Invalid mobile number",
            "status": "error"
        }), 400

    return jsonify({
        "message": "OTP Sent!",
        "status": "success"
    }), 201

@api_v2.route("/confirm-mobile", methods=["POST"])
def confirm_mobile():
    mobile_number = request.json.get('mobile_number')
    verification_code = request.json.get("otp")

    if not all((mobile_number)):
        return jsonify({
            "message": "Incomplete credentials",
            "status": "error"
        }), 400

    if not all((verification_code)):
        return jsonify({
            "message": "Please enter the OTP",
            "status": "error"
        }), 400

    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    verification_check = client.verify.services(os.environ.get("OTP_SERVICE_ID")).verification_checks.create(to=f"+91{mobile_number}", code=verification_code)

    if verification_check.status == "approved":
        user = User.query.filter_by(mobile_number=mobile_number).first()
        if not user:
            User.create('', '', mobile_number, '')
            user = User.query.filter_by(mobile_number=mobile_number).first()

        return jsonify({
            "redirect": url_for('views.add_details'),
            "status": "success",
            "user": user.to_json(),
        }), 201
    else:
        return jsonify({
            "message": "Verification Failed! Try Again.",
            "status": "error"
        }), 400

@api_v2.route("/choose-plan", methods=["POST"])
def choose_plan():
    mobile_number = request.json.get('mobile_number')
    plan = request.json.get("plan")

    if not mobile_number:
        return jsonify({"message": "No mobile number" }), 400

    user = User.query.filter_by(mobile_number=mobile_number).first()

    user.update_plan(plan)

    return jsonify({
        "redirect": url_for('views.selected_plan'),
        "status": "success"
    }), 201

@api_v2.route("/choose-plan-duration", methods=["POST"])
def choose_plan_duration():
    mobile_number = request.json.get('mobile_number')
    plan_duration = request.json.get("plan_duration")

    if not mobile_number:
        return jsonify({"message": "No mobile number" }), 400
    if int(plan_duration) not in [3, 6, 12]:
        return jsonify({"message": "Invalid plan duration" }), 400

    user = User.query.filter_by(mobile_number=mobile_number).first()

    user.plan_duration = plan_duration

    db.session.commit()

    return jsonify({
        "redirect": url_for('views.selected_plan'),
        "status": "success"
    }), 201

@api_v2.route("/change-plan", methods=["POST"])
def change_plan():
    mobile_number = request.json.get('mobile_number')

    if not mobile_number:
        return jsonify({"message": "No mobile number" }), 400

    user = User.query.filter_by(mobile_number=mobile_number).first()

    user.remove_plan()

    return jsonify({
        "redirect": url_for('views.select_plan'),
        "status": "success"
    }), 201

@api_v2.route("/generate-subscription-id", methods=["POST"])
def generate_subscription_id():
    mobile_number = request.json.get('mobile_number')
    if not mobile_number:
        return jsonify({"message": "No mobile number" }), 400
    user = User.query.filter_by(mobile_number=mobile_number).first()
    client = razorpay.Client(auth=(os.environ.get("RZP_KEY_ID"), os.environ.get("RZP_KEY_SECRET")))

    plan_name = ''
    if user.books_per_week == 1:
        plan_name = "RZP_PLAN_1_ID"
        plan_desc = "Get 1 Book Per Week"
    elif user.books_per_week == 2:
        plan_name = "RZP_PLAN_2_ID"
        plan_desc = "Get 2 Books Per Week"
    elif user.books_per_week == 4:
        plan_name = "RZP_PLAN_3_ID"
        plan_desc = "Get 4 Books Per Week"

    subscription = client.subscription.create({
        'plan_id': os.environ.get(plan_name),
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

@api_v2.route("/generate-order-id", methods=["POST"])
def generate_order_id():
    mobile_number = request.json.get('mobile_number')
    card = request.json.get('card')
    if not mobile_number:
        return jsonify({"message": "No mobile number" }), 400
    user = User.query.filter_by(mobile_number=mobile_number).first()
    client = razorpay.Client(auth=(os.environ.get("RZP_KEY_ID"), os.environ.get("RZP_KEY_SECRET")))

    if card not in [3, 6, 12]:
        return jsonify({
            "message": "Invalid card",
            "status": "error"
        }), 400

    client = razorpay.Client(auth=(os.environ.get("RZP_KEY_ID"), os.environ.get("RZP_KEY_SECRET")))

    amount = 0
    if user.plan_id == os.environ.get("RZP_PLAN_1_ID"): 
        if card == 3: 
            amount = 1199
        elif card == 6: 
            amount = 2199
        elif card == 12: 
            amount = 4199
        plan_desc = "Get 1 Book Per Week"
    elif user.plan_id == os.environ.get("RZP_PLAN_2_ID"): 
        if card == 3: 
            amount = 1799
        elif card == 6: 
            amount = 3399
        elif card == 12: 
            amount = 6399
        plan_desc = "Get 2 Books Per Week"
    elif user.plan_id == os.environ.get("RZP_PLAN_3_ID"):
        if card == 3: 
            amount = 2399
        elif card == 6: 
            amount = 4499
        elif card == 12: 
            amount = 8599
        plan_desc = "Get 4 Books Per Week"

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

@api_v2.route("/verify-subscription", methods=["POST"])
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

@api_v2.route("/verify-order", methods=["POST"])
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

@api_v2.route("/subscription-successful", methods=["POST"])
def subscription_successful():
    mobile_number = request.json.get('mobile_number')
    if not mobile_number:
        return jsonify({"message": "No mobile number" }), 400
    subscription_id = request.json.get("subscription_id")
    payment_id = request.json.get("payment_id")

    user = User.query.filter_by(mobile_number=mobile_number).first()
    user.password = '12345'

    user.update_subscription_details(subscription_id, payment_id)

    return jsonify({
        "status": "success"
    }), 201

@api_v2.route("/payment-successful", methods=["POST"])
def payment_successful():
    mobile_number = request.json.get('mobile_number')
    if not mobile_number:
        return jsonify({"message": "No mobile number" }), 400
    payment_id = request.json.get("payment_id")
    order_id = request.json.get("order_id")

    user = User.query.filter_by(mobile_number=mobile_number).first()
    user.password = '12345'

    user.update_payment_details(order_id, payment_id)

    return jsonify({
        "status": "success"
    }), 201

@api_v2.route("/change-password", methods=["POST"])
@token_required
def change_password(user):
    try:
        password = request.json.get("password")
        if not password or len(password) < 5:
            return jsonify({
                "message": "Password should be atleast of 5 characters",
                "status": "success"
            }), 400
        user.password = password
        db.session.commit();
        return jsonify({
            "status": "success"
        }), 200
    except Exception as e:
        print(e)
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api_v2.route("/forgot-password", methods=["POST"])
def forgot_password():
    try:
        mobile_number = request.json.get('mobile_number')
        password = request.json.get("password")
        confirm_password = request.json.get('confirm_password')
        otp = request.json.get('otp')
        user = User.query.filter_by(mobile_number=mobile_number).first()
        if not user:
            return jsonify({
                "message": "Invalid mobile number",
                "status": "success"
            }), 400
        if not password or len(password) < 5:
            return jsonify({
                "message": "Password should be atleast of 5 characters",
                "status": "success"
            }), 400
        if password != confirm_password:
            return jsonify({
                "message": "Passwords do not match",
                "status": "success"
            }), 400

        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token)

        verification_check = client.verify.services(os.environ.get("OTP_SERVICE_ID")).verification_checks.create(to=f"+91{user.mobile_number}", code=otp)

        if verification_check.status == "approved":
            user.password = password
            db.session.commit()
            return jsonify({
                "status": "success",
                "message": "Password updated"
            }), 200
        else:
            return jsonify({
                "message": "Verification Failed! Try Again.",
                "status": "error"
            }), 400
    except Exception as e:
        print(e)
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api_v2.route("/submit-preferences", methods=["POST"])
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

@api_v2.route('/get-user')
@token_required
def get_user(user):
    try:
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

@api_v2.route("/get-wishlists")
@token_required
def get_wishlists(user):
    try:
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

@api_v2.route("/get-suggestions")
@token_required
def get_suggestions(user):
    try:
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

@api_v2.route("/get-dumps")
@token_required
def get_dumps(user):
    try:
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

@api_v2.route('/get-previous-books')
@token_required
def get_previous_books(user):
    try:
        return jsonify({
            "status": "success",
            "books": user.get_previous_books()
        }), 200
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api_v2.route('/get-current-books')
@token_required
def get_current_books(user):
    try:
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

@api_v2.route("/get-buckets")
@token_required
def get_buckets(user):
    try:
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

@api_v2.route("/get-order-bucket")
@token_required
def get_order_bucket(user):
    try:
        if not user:
            return jsonify({
                "message": "User Not Found",
                "status": "error"
            }), 400
        return jsonify({
            "status": "success",
            "wishlists": user.get_order_bucket()
        }), 200

    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api_v2.route("/add-to-wishlist", methods=["POST"])
@token_required
def add_to_wishlist(user):
    isbn = request.json.get("isbn")
    try:
        if not user:
            return jsonify({
                "message": "User Not Found",
                "status": "error"
            }), 400

        user.add_to_wishlist(isbn)

        return jsonify({
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api_v2.route("/suggestion-to-wishlist", methods=["POST"])
@token_required
def suggestion_to_wishlist(user):
    isbn = request.json.get("isbn")
    try:
        if not user:
            return jsonify({
                "message": "User Not Found",
                "status": "error"
            }), 400

        user.suggestion_to_wishlist(isbn)

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

@api_v2.route("/suggestion-to-dump", methods=["POST"])
@token_required
def suggestion_to_dump(user):
    isbn = request.json.get("isbn")
    try:
        if not user:
            return jsonify({
                "message": "User Not Found",
                "status": "error"
            }), 400

        user.suggestion_to_dump(isbn)

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

@api_v2.route("/dump-action-read", methods=["POST"])
@token_required
def dump_action_read(user):
    isbn = request.json.get("isbn")
    try:
        if not user:
            return jsonify({
                "message": "User Not Found",
                "status": "error"
            }), 400

        user.dump_action_read(isbn)

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

@api_v2.route("/dump-action-dislike", methods=["POST"])
@token_required
def dump_action_dislike(user):
    isbn = request.json.get("isbn")
    try:
        if not user:
            return jsonify({
                "message": "User Not Found",
                "status": "error"
            }), 400

        user.dump_action_dislike(isbn)

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

@api_v2.route("/wishlist-next", methods=["POST"])
@token_required
def wishlist_next(user):
    isbn = request.json.get("isbn")
    try:
        if not user:
            return jsonify({
                "message": "User Not Found",
                "status": "error"
            }), 400

        user.wishlist_next(isbn)

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

@api_v2.route("/wishlist-prev", methods=["POST"])
@token_required
def wishlist_prev(user):
    isbn = request.json.get("isbn")
    try:
        if not user:
            return jsonify({
                "message": "User Not Found",
                "status": "error"
            }), 400

        user.wishlist_prev(isbn)

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

@api_v2.route("/wishlist-remove", methods=["POST"])
@token_required
def wishlist_remove(user):
    isbn = request.json.get("isbn")
    try:
        if not user:
            return jsonify({
                "message": "User Not Found",
                "status": "error"
            }), 400

        user.wishlist_remove(isbn)

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

@api_v2.route("/create-bucket-list")
@token_required
def create_bucket_list(user):
    try:
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

@api_v2.route("/bucket-remove", methods=["POST"])
@token_required
def bucket_remove(user):
    try:
        isbn = request.json.get("isbn")
        if not user:
            return jsonify({
                "message": "User Not Found",
                "status": "error"
            }), 400

        user.bucket_remove(isbn)
        return jsonify({
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api_v2.route("/change-delivery-date", methods=["POST"])
@token_required
def change_delivery_date(user):
    try:
        delivery_date = request.json.get("delivery_date")
        if not user:
            return jsonify({
                "message": "User Not Found",
                "status": "error"
            }), 400

        user.change_delivery_date(delivery_date)
        return jsonify({
            "status": "success",
            "user": user.to_json()
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api_v2.route("/confirm-order")
@token_required
def confirm_order(user):
    try:
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

@api_v2.route("/retain-book", methods=["POST"])
@token_required
def retain_book(user):
    isbn = request.json.get("isbn")
    try:
        if not user:
            return jsonify({
                "message": "User Not Found",
                "status": "error"
            }), 400

        user.retain_book(isbn)
        return jsonify({
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api_v2.route("/retain-current-book", methods=["POST"])
@token_required
def retain_current_book(user):
    try:
        isbn = request.json.get("isbn")
        if not user:
            return jsonify({
                "message": "User Not Found",
                "status": "error"
            }), 400

        user.retain_current_book(isbn)
        return jsonify({
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api_v2.route("/logout", methods=["POST"])
@token_required
def logout(user):
    response = make_response(jsonify({
        "message": "Success!",
        "status": "success"
    }), 201)
    response.set_cookie('access_token', '', secure=True, httponly=True, samesite='None')
    return response

@api_v2.route("/get-most-borrowed")
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

@api_v2.route("/get-bestsellers")
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

@api_v2.route("/get-authors")
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

@api_v2.route("/get-author-books")
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

@api_v2.route("/get-series")
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

@api_v2.route("/get-series-books")
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

@api_v2.route("/get-publishers")
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

@api_v2.route("/get-publisher-books")
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

@api_v2.route("/get-types")
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

@api_v2.route("/get-type-books")
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

@api_v2.route("/get-genres")
def get_genres():
    age_group = request.args.get("age")
    return jsonify({
        "data": Category.get_genres(age_group),
        "status": "success"
    }), 200

@api_v2.route("/get-genres-books", methods=["POST"])
def get_genres_books():
    guid = request.json.get("guid")
    return jsonify({
        "data": Book.get_genres_books(guid),
        "name": Category.query.filter_by(guid=guid).first().name,
        "status": "success"
    }), 200

@api_v2.route("/get-similar-books", methods=["POST"])
def get_similar_books():
    age_group = request.json.get("age_group")
    return jsonify({
        "data": Book.get_similar_books(age_group),
        "status": "success"
    }), 200

@api_v2.route("/submit-search-form", methods=["POST"])
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

@api_v2.route("/search")
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

@api_v2.route("/get-book-details")
def get_book_details():
    try:
        isbn = request.args.get("isbn")
        if not isbn:
            return jsonify({
                "message": "Book GUID is required!",
                "status": "error"
            }), 400

        book = Book.query.filter_by(isbn=isbn).first()

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
