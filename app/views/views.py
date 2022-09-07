from flask import Blueprint, jsonify, request, render_template, redirect, session, url_for

from app.models.annotations import Annotation
from app.models.author import Author
from app.models.books import Book
from app.models.category import Category
from app.models.details import Detail
from app.models.publishers import Publisher
from app.models.reviews import Review
from app.models.series import Series
from app.models.user import *
from app.models.buckets import *

import os
from datetime import date

views = Blueprint('views', __name__, url_prefix="/")

@views.route("/")
def home():
    return render_template(
        "home/home.html"
    )

@views.route("/signup")
def signup():
    mobile_number = session.get("mobile_number")
    if not mobile_number:
        return redirect(url_for('views.home'))
    return render_template(
        "signup_new/signup_new.html",
        mobile_number=mobile_number
    )

@views.route("/login")
def login():
    user = User.query.filter_by(mobile_number=session.get("mobile_number")).first()
    if not user:
        return redirect(url_for('views.home'))
    return render_template(
        "/login/login.html",
        user=user
    )

@views.route('/confirm-mobile')
def confirm_mobile():
    mobile_number = session.get("mobile_number")
    if not mobile_number:
        return redirect(url_for('views.home'))
    return render_template(
        "confirm_mobile_new/confirm_mobile_new.html",
        mobile_number=mobile_number
    )

@views.route("/add-details")
def add_details():
    user = User.query.filter_by(guid=session.get("current_user")).first()
    if not user:
        return redirect(url_for('views.home'))
    if user.password:
        return redirect(url_for('views.select_plan'))
    return render_template(
        "add_details/add_details.html",
        user=user
    )

@views.route("/select-plan")
def select_plan():
    user = User.query.filter_by(guid=session.get("current_user")).first()
    if not user:
        return redirect(url_for('views.home'))
    if not user.password:
        return redirect(url_for('views.add_details'))
    if user.plan_id:
        return redirect(url_for('views.selected_plan'))
    return render_template(
        "select_plan/select_plan.html"
    )

@views.route("/selected-plan")
def selected_plan():
    user = User.query.filter_by(guid=session.get("current_user")).first()
    if not user:
        return redirect(url_for('views.home'))
    if not user.plan_id:
        return redirect(url_for('views.select_plan'))
    if user.is_subscribed:
        return redirect(url_for('views.add_address'))

    if user.plan_id == os.environ.get("RZP_PLAN_1_ID"):
        plan_image = "selected1.svg"
    elif user.plan_id == os.environ.get("RZP_PLAN_2_ID"):
        plan_image = "selected2.svg"
    elif user.plan_id == os.environ.get("RZP_PLAN_3_ID"):
        plan_image = "selected3.svg"
    return render_template(
        "selected_plan/selected_plan.html",
        plan_image=plan_image
    )

@views.route("/confirm-subscription")
def confirm_subscription():
    user = User.query.filter_by(guid=session.get("current_user")).first()
    if not user:
        return redirect(url_for('views.home'))
    if not user.plan_id:
        return redirect(url_for('views.select_plan'))
    if user.is_subscribed:
        return redirect(url_for('views.add_address'))

    if user.plan_id == os.environ.get("RZP_PLAN_1_ID"):
        plan_image = "subscription_box1.svg"
        amount = 799
        next_amount = 299
    elif user.plan_id == os.environ.get("RZP_PLAN_2_ID"):
        plan_image = "subscription_box2.svg"
        amount = 949
        next_amount = 449
    elif user.plan_id == os.environ.get("RZP_PLAN_3_ID"):
        plan_image = "subscription_box3.svg"
        amount = 1169
        next_amount = 669
    return render_template(
        "confirm_subscription/confirm_subscription.html",
        plan_image=plan_image,
        amount=amount,
        next_amount=next_amount
    )

@views.route("/confirm-payment")
def confirm_payment():
    user = User.query.filter_by(guid=session.get("current_user")).first()
    if not user:
        return redirect(url_for('views.home'))
    if not user.plan_id:
        return redirect(url_for('views.select_plan'))
    if user.is_subscribed:
        return redirect(url_for('views.add_address'))

    if user.plan_id == os.environ.get("RZP_PLAN_1_ID"):
        plan_image = "payment_box1.svg"
        amount = 1379
        next_amount = 897
    elif user.plan_id == os.environ.get("RZP_PLAN_2_ID"):
        plan_image = "payment_box2.svg"
        amount = 1847
        next_amount = 1347
    elif user.plan_id == os.environ.get("RZP_PLAN_3_ID"):
        plan_image = "payment_box3.svg"
        amount = 2507
        next_amount = 2007
    return render_template(
        "confirm_payment/confirm_payment.html",
        plan_image=plan_image,
        amount=amount,
        next_amount=next_amount
    )

@views.route("/payment-failed")
def payment_failed():
    user = User.query.filter_by(guid=session.get("current_user")).first()
    if not user:
        return redirect(url_for('views.home'))
    if user.is_subscribed:
        return redirect(url_for('views.add_address'))
    return render_template(
        "/payment_failed/payment_failed.html"
    )

@views.route("/payment-successful")
def payment_successful():
    user = User.query.filter_by(guid=session.get("current_user")).first()
    if not user:
        return redirect(url_for('views.home'))
    if not user.is_subscribed:
        return redirect(url_for('views.select_plan'))
    return render_template(
        "/payment_successful/payment_successful.html",
        payment_id=user.payment_id
    )

@views.route("/add-address")
def add_address():
    user = User.query.filter_by(guid=session.get("current_user")).first()
    if not user:
        return redirect(url_for('views.home'))
    if not user.is_subscribed:
        return redirect(url_for('views.select_plan'))
    if len(user.address) > 0:
        return redirect(url_for('views.add_children'))
    return render_template(
        "/add_address/add_address.html",
    )

@views.route("/add-children")
def add_children():
    user = User.query.filter_by(guid=session.get("current_user")).first()
    if not user:
        return redirect(url_for('views.home'))
    if len(user.address) == 0:
        return redirect(url_for('views.add_address'))
    if len(user.child) > 0:
        return redirect(url_for('views.preferences'))
    return render_template(
        "/add_children/add_children.html",
        user=user
    )

@views.route("/preferences")
def preferences():
    user = User.query.filter_by(guid=session.get("current_user")).first()
    if not user:
        return redirect(url_for('views.home'))
    if len(user.child) == 0:
        return redirect(url_for('views.add_children'))

    all_preferences = True
    for child in user.child:
        if not child.preferences:
            all_preferences = False
    
    if all_preferences:
        return redirect(url_for('views.library'))
    else:
        guid = request.args.get("guid")
        all_children = Child.query.filter_by(user_id=user.id).order_by(Child.dob.desc()).all()
        for child in user.child:
            if guid == child.guid:
                if child.preferences:
                    return render_template(
                        "/preferences/preferences.html",
                        guid=guid,
                        child=child,
                        all_children=all_children,
                        position=all_children.index(child),
                        categories=[category.guid for category in child.preferences.categories],
                        formats=[format_obj.guid for format_obj in child.preferences.formats],
                        authors=[authors.guid for authors in child.preferences.authors],
                        series=[serie.guid for serie in child.preferences.series]
                    )
                else:
                    return render_template(
                        "/preferences/preferences.html",
                        guid=guid,
                        child=child,
                        all_children=all_children,
                        position=all_children.index(child),
                        categories=[],
                        formats=[],
                        authors=[],
                        series=[]
                    )
        if user.child[0].preferences:
            return render_template(
                "/preferences/preferences.html",
                guid=user.child[0].guid,
                child=user.child[0],
                all_children=all_children,
                position=all_children.index(user.child[0]),
                categories=[category.guid for category in user.child[0].preferences.categories],
                formats=[format_obj.guid for format_obj in user.child[0].preferences.formats],
                authors=[authors.guid for authors in user.child[0].preferences.authors],
                series=[serie.guid for serie in user.child[0].preferences.series]
            )
        else:
            return render_template(
                "/preferences/preferences.html",
                guid=user.child[0].guid,
                child=user.child[0],
                all_children=all_children,
                position=all_children.index(user.child[0]),
                categories=[],
                formats=[],
                authors=[],
                series=[]
            )

@views.route("/library")
def library():
    user = User.query.filter_by(guid=session.get("current_user")).first()
    if not user:
        return redirect(url_for('views.home'))
    if len(user.child) == 0:
        return redirect(url_for('views.add_children'))

    all_preferences = True
    for child in user.child:
        if not child.preferences:
            all_preferences = False
    
    if not all_preferences:
        return redirect(url_for('views.preferences'))

    if user.next_delivery_date:
        next_delivery_date = user.next_delivery_date.strftime("%A %d %B %Y")
        next_delivery_date_input = user.next_delivery_date.strftime("%Y-%m-%d")
    else:
        next_delivery_date = date.today().strftime("%A %d %B %Y")
        next_delivery_date_input = date.today().strftime("%Y-%m-%d")
    all_children = Child.query.filter_by(user_id=user.id).order_by(Child.dob.desc()).all()
    return render_template(
        "/library/library.html",
        all_children=all_children,
        # next_bucket=user.get_next_bucket(),
        next_bucket=[],
        retain_books=user.get_previous_books(),
        # retain_books=[],
        suggestions=user.get_suggestions(),
        wishlists=user.get_wishlist(),
        read_books=user.get_read_books(),
        dumps=user.get_dump_data(),
        next_delivery_date=next_delivery_date,
        next_delivery_date_input=next_delivery_date_input,
        user=user
    )

@views.route("/browse")
def browse():
    return render_template(
        "/home_new/home_new.html"
    )

# @views.route("/happy-reading")
# def happy_reading():
#     user = User.query.filter_by(guid=session.get("current_user")).first()
#     if not user:
#         return redirect(url_for('views.home'))
#     if len(user.child) == 0:
#         return redirect(url_for('views.add_children'))
#     return render_template(
#         "happy_reading/happy_reading.html",
#         user=user
#     )

@views.route("/terms-and-conditions")
def terms_and_conditions():
    return render_template(
        "/terms_and_conditions/terms_and_conditions.html"
    )

@views.route("/privacy-policy")
def privacy_policy():
    return render_template(
        "/privacy_policy/privacy_policy.html"
    )

@views.route("/disclaimer")
def disclaimer():
    return render_template(
        "/disclaimer/disclaimer.html"
    )

@views.route("/refund-policy")
def refund_policy():
    return render_template(
        "/refund_policy/refund_policy.html"
    )

@views.route("/contact-us")
def contact_us():
    return render_template(
        "/contact_us/contact_us.html"
    )

@views.route("/about-us")
def about_us():
    return render_template(
        "/about_us/about_us.html"
    )


################################### Admin APIs (Temporary)
@views.route("/delete-user")
def delete_user():
    guid = request.args.get("guid")
    mobile_number = request.args.get("mobile_number")

    if guid != "8cfa1920-dff4-4c7f-a928-d64f9e147f69":
        return "Incorrect GUID"
    
    if mobile_number not in ["9910402972", "8826144375", "9953865517"]:
        return "This mobile number cannot be resetted"

    user = User.query.filter_by(mobile_number=mobile_number).first()
    
    if not user:
        return "User not found"

    for child in user.child:
        child.delete()

    user.delete()

    return redirect(url_for("views.home"))

@views.route("/mark-paid")
def mark_paid():
    guid = request.args.get("guid")
    mobile_number = request.args.get("mobile_number")

    if guid != "74ae9792-b094-4877-8c92-dd155c5428d1":
        return "Incorrect GUID"
    
    if mobile_number not in ["9910402972", "8826144375", "9953865517"]:
        return "This mobile number cannot be marked as paid"

    user = User.query.filter_by(mobile_number=mobile_number).first()

    user.update_payment_details("testing", "testing")

    return redirect(url_for("views.add_address"))

@views.route("/get-user-data")
def get_user_data():
    guid = request.args.get("guid")

    if guid != "4b5490ff-dd63-41ab-8f15-c1e3b5758fd9":
        return "Incorrect GUID"

    users = User.query.all()
    addresses = Address.query.all()
    children = Child.query.all()

    return jsonify({
        "users": [
            {
                "id": user.id,
                "guid": user.guid,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "mobile_number": user.mobile_number,
                "email": user.email,
                "is_subscribed": user.is_subscribed,
                "security_deposit": user.security_deposit,
                "payment_id": user.payment_id,
                "plan_id": user.plan_id,
                "subscription_id": user.subscription_id,
                "order_id": user.order_id,
            } for user in users
        ],
        "addresses": [
            {
                "guid": address.guid,
                "house_number": address.house_number,
                "building": address.building,
                "area": address.area,
                "pincode": address.pincode,
                "landmark": address.landmark,
                "user_id": address.user_id
            } for address in addresses
        ],
        "children": [
            {
                "guid": child.guid,
                "name": child.name,
                "dob": child.dob,
                "age_group": child.age_group,
                "user_id": child.user_id,
            } for child in children
        ]
    }), 200

@views.route("/get-wishlist")
def get_wishlist_data():
    users = User.query.filter_by(is_subscribed=True).all()

    data = {}

    for user in users:
        data[user.mobile_number] = []
        wishlists = user.get_wishlist()[:4]
        for wishlist in wishlists:
            data[user.mobile_number].append(wishlist.book.isbn)

    return jsonify({
        "data": data
    }), 200

@views.route("/book-details")
def book_details():
    guid = request.args.get("guid")
    book = Book.query.filter_by(guid=guid).first()

    age_group = book.details.age_group

    current_user = session.get("current_user")
    user = None
    if current_user:
        user = User.query.filter_by(guid=guid).first()
    return render_template(
        "/details/detail.html",
        book=book,
        age_group=age_group,
        current_user=current_user,
        user=user
    )

@views.route('/confirm-plan')
def confirm_plan():
    plan = session.get("plan")
    if plan == 1:
        weekly_books = 1
        monthly_books = 4
        price_month = 299
    elif plan == 2:
        weekly_books = 2
        monthly_books = 8
        price_month = 449
    else:
        weekly_books = 4
        monthly_books = 16
        price_month = 669
    security_deposit = 500
    total_payable_amount = price_month + security_deposit

    current_user = session.get("current_user")
    return render_template(
        "/confirm_plan/confirm_plan.html",
        weekly_books=weekly_books,
        monthly_books=monthly_books,
        price_month=price_month,
        security_deposit=security_deposit,
        total_payable_amount=total_payable_amount,
        plan=plan,
        current_user=current_user
    )

# @views.route("/cart")
# def cart():
#     current_user_guid = session.get('current_user')
#     if current_user_guid:
#         current_user = User.query.filter_by(guid=current_user_guid).first()
#         cart_objs = current_user.cart.books
#         wishlist_objs = current_user.wishlist.books
#     else:
#         cart = session.get("cart") or []
#         cart_objs = []
#         for item in cart:
#             cart_objs.append(Book.query.filter_by(guid=item).first())

#         wishlist = session.get("wishlist") or []
#         wishlist_objs = []
#         for item in wishlist:
#             wishlist_objs.append(Book.query.filter_by(guid=item).first())
#     current_user = session.get("current_user")
#     return render_template(
#         "/cart/cart.html",
#         cart = cart_objs,
#         wishlist = wishlist_objs,
#         current_user=current_user
#     )

@views.route("/order-placed")
def order_placed():
    current_user = session.get("current_user")
    return render_template(
        "/order_placed/order_placed.html",
        current_user=current_user
    )

@views.route("/search-result")
def search_result():
    search = request.args.get("query")
    all_books = Book.query.filter(Book.name.ilike(f"%{search}%")).all()
    all_authors = Author.query.filter(Author.name.like(f"%{search}%")).all()
    all_publishers = Publisher.query.filter(Publisher.name.like(f"%{search}%")).all()
    current_user = session.get("current_user")
    user = None
    if current_user:
        user = User.query.filter_by(guid=session.get("current_user")).first()
    return render_template(
        "/search_result/search_result.html",
        current_user = current_user,
        all_books = all_books,
        all_authors = all_authors,
        all_publishers = all_publishers,
        query = search,
        user = user
    )