from flask import Blueprint, jsonify, request, render_template, redirect, session, url_for

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

import os
from twilio.rest import Client

import razorpay

api = Blueprint('api', __name__, url_prefix="/api")

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
            "status": "success"
        }), 200
    elif user:
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token)

        verification = client.verify.services(os.environ.get('OTP_SERVICE_ID')).verifications.create(to=f"+91{mobile_number}", channel="sms")

        return jsonify({
            "redirect": url_for('views.confirm_mobile'),
            "status": "success"
        }), 200
    else:
        return jsonify({
            "redirect": url_for('views.signup'),
            "status": "success"
        }), 200

@api.route("/login", methods=["POST"])
def login():
    mobile_number = session.get("mobile_number")
    password = request.json.get("password")

    if not all((password)):
        return jsonify({
            "message": "Password not entered!",
            "status": "error"
        }), 400

    user = User.query.filter_by(mobile_number=mobile_number).first()

    if user:
        if user.password == password:
            session["current_user"] = user.guid
            if not user.plan_id:
                return jsonify({
                    "redirect": url_for("views.select_plan"),
                    "status": "success"
                }), 200
            if user.plan_id and not user.is_subscribed:
                return jsonify({
                    "redirect": url_for('views.selected_plan'),
                    "status": "success"
                }), 200
            if len(user.address) == 0:
                return jsonify({
                    "redirect": url_for('views.add_address'),
                    "status": "success"
                }), 200
            if len(user.child) == 0:
                return jsonify({
                    "redirect": url_for('views.add_children'),
                    "status": "success"
                }), 200
            return jsonify({
                "redirect": url_for('views.preferences'),
                "status": "success"
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

    if not all((first_name)):
        return jsonify({
            "message": "First Name is mandatory!",
            "status": "error"
        }), 400

    session["first_name"] = first_name
    session["last_name"] = last_name

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

    verification = client.verify.services(os.environ.get('OTP_SERVICE_ID')).verifications.create(to=f"+91{session.get('mobile_number')}", channel="sms")

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

    verification_check = client.verify.services(os.environ.get("OTP_SERVICE_ID")).verification_checks.create(to=f"+91{session.get('mobile_number')}", code=verification_code)

    if verification_check.status == "approved":
        user = User.query.filter_by(mobile_number=session.get("mobile_number")).first()
        if not user:
            User.create(session.get("first_name"), session.get("last_name"), session.get("mobile_number"))
            user = User.query.filter_by(mobile_number=session.get("mobile_number")).first()

            session["first_name"] = None
            session["last_name"] = None
            session["mobile_number"] = None

        session["current_user"] = user.guid

        return jsonify({
            "redirect": url_for('views.add_details'),
            "status": "success"
        }), 201
    else:
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

    user = User.query.filter_by(guid=session.get("current_user")).first()

    user.update_plan(plan)

    return jsonify({
        "redirect": url_for('views.selected_plan'),
        "status": "success"
    }), 201

@api.route("/change-plan", methods=["POST"])
def change_plan():
    user = User.query.filter_by(guid=session.get("current_user")).first()

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
    user = User.query.filter_by(guid=session.get("current_user")).first()
    client = razorpay.Client(auth=(os.environ.get("RZP_KEY_ID"), os.environ.get("RZP_KEY_SECRET")))

    if user.plan_id == os.environ.get("RZP_PLAN_1_ID"):
        plan_desc = "Get 1 Book Per Week"
    elif user.plan_id == os.environ.get("RZP_PLAN_2_ID"):
        plan_desc = "Get 2 Books Per Week"
    elif user.plan_id == os.environ.get("RZP_PLAN_3_ID"):
        plan_desc = "Get 4 Books Per Week"

    subscription = client.subscription.create({
        'plan_id': user.plan_id,
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
    user = User.query.filter_by(guid=session.get("current_user")).first()
    client = razorpay.Client(auth=(os.environ.get("RZP_KEY_ID"), os.environ.get("RZP_KEY_SECRET")))

    if user.plan_id == os.environ.get("RZP_PLAN_1_ID"):
        amount = 137900
        plan_desc = "Get 1 Book Per Week"
    elif user.plan_id == os.environ.get("RZP_PLAN_2_ID"):
        amount = 184700
        plan_desc = "Get 2 Books Per Week"
    elif user.plan_id == os.environ.get("RZP_PLAN_3_ID"):
        amount = 250700
        plan_desc = "Get 4 Books Per Week"

    order = client.order.create({
        "amount": amount,
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

    user = User.query.filter_by(guid=session.get("current_user")).first()
    
    user.update_subscription_details(subscription_id, payment_id)

    return jsonify({
        "status": "success"
    }), 201

@api.route("/payment-successful", methods=["POST"])
def payment_successful():
    payment_id = request.json.get("payment_id")
    order_id = request.json.get("order_id")

    user = User.query.filter_by(guid=session.get("current_user")).first()
    
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

        # age_groups = []
        # for child in children:
        #     age_groups.append(child.get("age_group"))

        # age_groups = list(set(age_groups))

        # user.add_age_groups(age_groups)

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
def submit_preferences():
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
                preference_data.get("categories"),
                preference_data.get("formats"),
                preference_data.get("authors"),
                preference_data.get("series"),
                child.id
            )

        user = User.query.filter_by(guid=session.get("current_user")).first()
        for child_obj in user.child:
            if not child_obj.preferences:
                return jsonify({
                    "redirect": f"{url_for('views.preferences')}?guid={child_obj.guid}"
                }), 201
        return jsonify({
            "redirect": url_for('views.happy_reading')
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/suggestion-to-wishlist", methods=["POST"])
def suggestion_to_wishlist():
    try:
        guid = request.json.get("guid")
        user = User.query.filter_by(guid=session.get("current_user")).first()
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
def suggestion_to_dump():
    try:
        guid = request.json.get("guid")
        user = User.query.filter_by(guid=session.get("current_user")).first()
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
def dump_action_read():
    try:
        guid = request.json.get("guid")
        user = User.query.filter_by(guid=session.get("current_user")).first()
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
def dump_action_dislike():
    try:
        guid = request.json.get("guid")
        user = User.query.filter_by(guid=session.get("current_user")).first()
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
def wishlist_next():
    try:
        guid = request.json.get("guid")
        user = User.query.filter_by(guid=session.get("current_user")).first()
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
def wishlist_prev():
    try:
        guid = request.json.get("guid")
        user = User.query.filter_by(guid=session.get("current_user")).first()
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
def wishlist_remove():
    try:
        guid = request.json.get("guid")
        user = User.query.filter_by(guid=session.get("current_user")).first()
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

@api.route("/bucket-remove", methods=["POST"])
def bucket_remove():
    try:
        guid = request.json.get("guid")
        user = User.query.filter_by(guid=session.get("current_user")).first()
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
def change_delivery_date():
    try:
        delivery_date = request.json.get("delivery_date")
        user = User.query.filter_by(guid=session.get("current_user")).first()
        user.change_delivery_date(delivery_date)
        return jsonify({
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/confirm-order", methods=["POST"])
def confirm_order():
    try:
        user = User.query.filter_by(guid=session.get("current_user")).first()
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
def retain_book():
    try:
        guid = request.json.get("guid")
        user = User.query.filter_by(guid=session.get("current_user")).first()
        user.retain_book(guid)
        return jsonify({
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/logout", methods=["POST"])
def logout():
    session["current_user"] = None
    return jsonify({
        "message": "Success!",
        "status": "success"
    }), 201

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

@api.route("/get-amazon-bestsellers", methods=["POST"])
def get_amazon_bestsellers():
    age_group = request.json.get("age_group")
    return jsonify({
        "data": Book.get_amazon_bestsellers(age_group),
        "status": "success"
    }), 200

@api.route("/get-all-amazon-bestsellers", methods=["POST"])
def get_all_amazon_bestsellers():
    try:
        age_group = request.json.get("age_group")
        return jsonify({
            "data": Book.get_all_amazon_bestsellers(age_group),
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "data": [],
            "status": "success"
        }), 200

@api.route("/get-most-borrowed", methods=["POST"])
def get_most_borrowed():
    age_group = request.json.get("age_group")
    return jsonify({
        "data": Book.get_most_borrowed(age_group),
        "status": "success"
    }), 200

@api.route("/get-all-most-borrowed", methods=["POST"])
def get_all_most_borrowed():
    try:
        age_group = request.json.get("age_group")
        return jsonify({
            "data": Book.get_all_most_borrowed(age_group),
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "data": [],
            "status": "success"
        }), 200

@api.route("/get-authors", methods=["POST"])
def get_authors():
    age_group = request.json.get("age_group")
    return jsonify({
        "data": Author.get_authors(age_group),
        "status": "success"
    }), 200

@api.route("/get-all-authors", methods=["POST"])
def get_all_authors():
    age_group = request.json.get("age_group")
    return jsonify({
        "data": Author.get_all_authors(age_group),
        "status": "success"
    }), 200

@api.route("/get-publishers", methods=["POST"])
def get_publishers():
    age_group = request.json.get("age_group")
    return jsonify({
        "data": Publisher.get_publishers(age_group),
        "status": "success"
    }), 200

@api.route("/get-all-publishers", methods=["POST"])
def get_all_publishers():
    age_group = request.json.get("age_group")
    return jsonify({
        "data": Publisher.get_all_publishers(age_group),
        "status": "success"
    }), 200

@api.route("/get-author-books", methods=["POST"])
def get_author_books():
    author = request.json.get("author")
    return jsonify({
        "data": Book.get_author_books(author),
        "status": "success"
    }), 200

@api.route("/get-publisher-books", methods=["POST"])
def get_publisher_books():
    publisher = request.json.get("publisher")
    return jsonify({
        "data": Book.get_publisher_books(publisher),
        "status": "success"
    }), 200

@api.route("/get-series-books", methods=["POST"])
def get_series_books():
    series = request.json.get("series")
    return jsonify({
        "data": Book.get_series_books(series),
        "status": "success"
    }), 200

@api.route("/get-series", methods=["POST"])
def get_series():
    age_group = request.json.get("age_group")
    return jsonify({
        "data": Series.get_series(age_group),
        "status": "success"
    }), 200

@api.route("/get-all-series", methods=["POST"])
def get_all_series():
    age_group = request.json.get("age_group")
    return jsonify({
        "data": Series.get_all_series(age_group),
        "status": "success"
    }), 200

@api.route("/get-genres", methods=["POST"])
def get_genres():
    age_group = request.json.get("age_group")
    return jsonify({
        "data": Category.get_genres(age_group),
        "status": "success"
    }), 200

@api.route("/get-all-genres", methods=["POST"])
def get_all_genres():
    age_group = request.json.get("age_group")
    return jsonify({
        "data": Category.get_all_genres(age_group),
        "status": "success"
    }), 200

@api.route("/get-formats", methods=["POST"])
def get_formats():
    age_group = request.json.get("age_group")
    return jsonify({
        "data": Format.get_formats(age_group),
        "status": "success"
    }), 200

@api.route("/get-genres-books", methods=["POST"])
def get_genres_books():
    genres = request.json.get("genres")
    return jsonify({
        "data": Book.get_genres_books(genres),
        "status": "success"
    }), 200

@api.route("/get-similar-books", methods=["POST"])
def get_similar_books():
    age_group = request.json.get("age_group")
    return jsonify({
        "data": Book.get_similar_books(age_group),
        "status": "success"
    }), 200

@api.route("/search", methods=["POST"])
def search():
    search = request.json.get("search")
    all_books = Book.query.filter(Book.name.like(f"%{search}%")).all()
    all_authors = Author.query.filter(Author.name.like(f"%{search}%")).all()
    all_publishers = Publisher.query.filter(Publisher.name.like(f"%{search}%")).all()
    return jsonify({
        "books": all_books,
        "authors": all_authors,
        "publishers": all_publishers,
        "status": "success"
    }), 200

@api.route("/submit-search-form", methods=["POST"])
def submit_search_form():
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