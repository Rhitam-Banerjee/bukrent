from flask import Blueprint, jsonify, request, render_template, redirect, session, url_for

from app.models.launch import Launch
from app.models.books import Book
from app.models.user import User, Address
from app.models.order import Order
from app.models.cart import Cart, Wishlist

import os
from twilio.rest import Client

import razorpay

api = Blueprint('api', __name__, url_prefix="/api")

@api.route("/login", methods=["POST"])
def login():
    mobile_number = request.json.get("mobile_number")

    if not mobile_number:
        return jsonify({
            "message": "No Mobile Number Added!",
            "status": "error"
        }), 400

    if len(mobile_number) != 10:
        return jsonify({
            "message": "Incorrect format for mobile number. Please make sure there are no spaces or country codes.",
            "status": "error"
        }), 400

    user = User.query.filter_by(mobile_number=mobile_number).first()
    if not user:
        return jsonify({
            "message": "No User with that mobile number exists!",
            "status": "error"
        }), 400

    session["mobile_number"] = mobile_number

    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    verification = client.verify.services(os.environ.get('OTP_SERVICE_ID')).verifications.create(to=f"+91{mobile_number}", channel="sms")

    return jsonify({
        "message": "OTP Sent!",
        "status": "success"
    }), 201

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

    user = User.query.filter_by(mobile_number=mobile_number).first()
    if user:
        session["mobile_number"] = mobile_number
    else:
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
        user = User.query.filter_by(mobile_number=session.get("mobile_number")).first()
        if not user:
            User.create(session.get("first_name"), session.get("last_name"), session.get("mobile_number"), session.get("newsletter"))
            user = User.query.filter_by(mobile_number=session.get("mobile_number")).first()

            session["first_name"] = None
            session["last_name"] = None
            session["newsletter"] = None
            session["mobile_number"] = None

            session["current_user"] = user.guid
        else:
            session["mobile_number"] = None
            session["current_user"] = user.guid
        
        user.add_books_to_cart_and_wishlist(session.get("cart") or [], session.get("wishlist") or [])
        session["cart"] = None
        session["wishlist"] = None

        if user.is_subscribed:
            return jsonify({
                "redirect": url_for('views.test'),
                "status": "success"
            }), 201
        else:
            if session.get("plan"):
                return jsonify({
                    "redirect": url_for('views.confirm_plan'),
                    "status": "success"
                }), 201
            else:
                return jsonify({
                    "redirect": url_for('views.become_a_subscriber'),
                    "status": "success"
                }), 201
        return jsonify({
            "message": "Success!",
            "status": "success"
        }), 201
        
    else:
        return jsonify({
            "message": "Verification Failed! Try Again.",
            "status": "error"
        }), 400

@api.route("/logout", methods=["POST"])
def logout():
    session["current_user"] = None
    return jsonify({
        "message": "Success!",
        "status": "success"
    }), 201

@api.route("/cart-checkout", methods=["POST"])
def cart_checkout():
    session["cart_checkout"] = True

    current_user = session.get("current_user")
    user = User.query.filter_by(guid=current_user).first()

    if current_user:
        if user.is_subscribed:
            return jsonify({
                "redirect": url_for('views.add_address'),
                "status": "success"
            }), 201
        else:
            if session.get("plan"):
                return jsonify({
                    "redirect": url_for('views.confirm_plan'),
                    "status": "success"
                }), 201
            else:
                return jsonify({
                    "redirect": url_for('views.become_a_subscriber'),
                    "status": "success"
                }), 201
    else:
        return jsonify({
            "redirect": url_for('views.signup'),
            "status": "success"
        }), 201

@api.route("/choose-plan", methods=["POST"])
def choose_plan():
    plan = request.json.get("plan")

    current_user = session.get("current_user")
    user = User.query.filter_by(guid=current_user).first()

    if current_user:
        if user.is_subscribed:
            return jsonify({
                "redirect": url_for('views.test'),
                "status": "success"
            }), 201
        else:
            session["plan"] = plan
            return jsonify({
                "redirect": url_for('views.confirm_plan'),
                "status": "success"
            }), 201
    else:
        session["plan"] = plan
        return jsonify({
            "redirect": url_for('views.signup'),
            "status": "success"
        }), 201

@api.route("/generate-subscription-id", methods=["POST"])
def generate_subscription_id():
    plan = session.get("plan")
    if not plan:
        return jsonify({
            "message": "No Plan Selected!",
            "status": "error"
        }), 400
    
    client = razorpay.Client(auth=(os.environ.get("RZP_KEY_ID"), os.environ.get("RZP_KEY_SECRET")))

    if plan == 1:
        plan_id = os.environ.get("RZP_PLAN_1_ID")
        plan_desc = "Get 1 Book Per Week"
    elif plan == 2:
        plan_id = os.environ.get("RZP_PLAN_2_ID")
        plan_desc = "Get 2 Books Per Week"
    elif plan == 3:
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
    session["plan"] = None

    if session.get("cart_checkout"):
        session["cart_checkout"] = None
        return redirect(url_for("views.add_address"))
    else:
        return redirect(url_for("views.payment_successful"))

@api.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    book_guid = request.json.get("guid")
    book = Book.query.filter_by(guid=book_guid).first()
    current_user_guid = session.get("current_user")
    if current_user_guid:
        current_user = User.query.filter_by(guid=session.get("current_user")).first()
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        cart.add_book(book)
    else:
        if session.get("cart"):
            cart = session.get("cart")
            cart.append(book.guid)
            session["cart"] = cart
        else:
            session["cart"] = [book.guid]

    return jsonify({
        "message": "Added",
        "status": "success"
    }), 201

@api.route("/add-to-wishlist", methods=["POST"])
def add_to_wishlist():
    book_guid = request.json.get("guid")
    book = Book.query.filter_by(guid=book_guid).first()
    current_user_guid = session.get("current_user")
    if current_user_guid:
        current_user = User.query.filter_by(guid=session.get("current_user")).first()
        wishlist = Wishlist.query.filter_by(user_id=current_user.id).first()
        wishlist.add_book(book)
    else:
        if session.get("wishlist"):
            wishlist = session.get("wishlist")
            wishlist.append(book.guid)
            session["wishlist"] = wishlist
        else:
            session["wishlist"] = [book.guid]

    return jsonify({
        "message": "Added",
        "status": "success"
    }), 201

@api.route("/move-to-wishlist", methods=["POST"])
def move_to_wishlist():
    book_guid = request.json.get('guid')
    book = Book.query.filter_by(guid=book_guid).first()
    current_user_guid = session.get("current_user")
    if current_user_guid:
        current_user = User.query.filter_by(guid=current_user_guid).first()
        current_user.move_book_to_wishlist(book)
    else:
        cart = session.get("cart")
        cart.remove(book_guid)
        session["cart"] = cart
        if session.get("wishlist"):
            wishlist = session.get("wishlist")
            wishlist.append(book_guid)
            session["wishlist"] = wishlist
        else:
            session["wishlist"] = [book_guid]
    return jsonify({
        "message": "Moved",
        "status": "success"
    }), 201

@api.route("/move-to-cart", methods=["POST"])
def move_to_cart():
    book_guid = request.json.get('guid')
    book = Book.query.filter_by(guid=book_guid).first()
    current_user_guid = session.get("current_user")
    if current_user_guid:
        current_user = User.query.filter_by(guid=current_user_guid).first()
        current_user.move_book_to_cart(book)
    else:
        wishlist = session.get("wishlist")
        wishlist.remove(book_guid)
        session["wishlist"] = wishlist
        if session.get("cart"):
            cart = session.get("cart")
            cart.append(book_guid)
            session["cart"] = cart
        else:
            session["cart"] = [book_guid]
    return jsonify({
        "message": "Moved",
        "status": "success"
    }), 201

@api.route("/delete-from-cart", methods=["POST"])
def delete_from_cart():
    book_guid = request.json.get('guid')
    book = Book.query.filter_by(guid=book_guid).first()
    current_user_guid = session.get("current_user")
    if current_user_guid:
        current_user = User.query.filter_by(guid=current_user_guid).first()
        current_user.remove_book_from_cart(book)
    else:
        cart = session.get("cart")
        cart.remove(book_guid)
        session["cart"] = cart
    return jsonify({
        "message": "Moved",
        "status": "success"
    }), 201

@api.route("/delete-from-wishlist", methods=["POST"])
def delete_from_wishlist():
    book_guid = request.json.get('guid')
    book = Book.query.filter_by(guid=book_guid).first()
    current_user_guid = session.get("current_user")
    if current_user_guid:
        current_user = User.query.filter_by(guid=current_user_guid).first()
        current_user.remove_book_from_wishlist(book)
    else:
        wishlist = session.get("wishlist")
        wishlist.remove(book_guid)
        session["wishlist"] = wishlist
    return jsonify({
        "message": "Moved",
        "status": "success"
    }), 201

@api.route("/check-books", methods=["POST"])
def check_books():
    current_user = session.get("current_user")
    user = User.query.filter_by(guid=current_user).first()
    if len(user.cart.books) < user.books_per_week:
        return jsonify({
            "message": f"You should have at least {user.books_per_week} books in your cart to place an order.",
            "status": "error"
        }), 400
    else:
        return jsonify({
            "status": "success"
        }), 200

@api.route("/place-order", methods=["POST"])
def place_order():
    try:
        current_user = session.get("current_user")
        user = User.query.filter_by(guid=current_user).first()

        if user.books_per_week != len(request.json.get("books")):
            return jsonify({
                "message": f"Select {user.books_per_week} books to place an order.",
                "status": "error"
            }), 400

        billing_address = Address.create(request.json.get("billing_address"), user.id)
        if request.json.get("same_as_billing"):
            delivery_address = billing_address
        else:
            delivery_address = Address.create(request.json.get("delivery_address"), user.id)
        
        is_gift = request.json.get("is_gift")
        gift_message = request.json.get("gift_message")
        books = request.json.get("books")

        Order.create(user.id, billing_address.id, delivery_address.id, is_gift, gift_message, books)
        for book in books:
            user.remove_book_from_cart(Book.query.filter_by(guid=book).first())

        return jsonify({
            "message": "Order Placed",
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({
            "message": str(e),
            "status": "error"
        }), 400

@api.route("/get-amazon-bestsellers", methods=["POST"])
def get_amazon_bestsellers():
    age_group = request.json.get("age_group")
    return jsonify({
        "data": Book.get_amazon_bestsellers(age_group),
        "status": "success"
    }), 200

@api.route("/get-most-borrowed", methods=["POST"])
def get_most_borrowed():
    age_group = request.json.get("age_group")
    return jsonify({
        "data": Book.get_most_borrowed(age_group),
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