from flask import Blueprint, jsonify, request, render_template, redirect, session, url_for

from app.models.annotations import Annotation
from app.models.author import Author
from app.models.books import Book
from app.models.category import Category
from app.models.details import Detail
from app.models.publishers import Publisher
from app.models.reviews import Review
from app.models.series import Series
from app.models.user import User
from app.models.cart import Cart, Wishlist

views = Blueprint('views', __name__, url_prefix="/")

@views.route("/")
def home():
    current_user = session.get("current_user")
    return render_template(
        "/home_new/home_new.html",
        current_user=current_user
    )

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

@views.route('/become-subscriber')
def become_a_subscriber():
    current_user = session.get("current_user")
    return render_template(
        "/become_subscriber/become_subscriber.html",
        current_user=current_user
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

@views.route("/signup")
def signup():
    if session.get("current_user"):
        user = User.query.filter_by(guid=session.get("current_user")).first()
        if user.is_subscribed:
            redirect(url_for('views.cart'))
        else:
            redirect(url_for(''))
    current_user = session.get("current_user")
    return render_template(
        "/signup/signup.html",
        current_user=current_user
    )

@views.route("/login")
def login():
    current_user = session.get("current_user")
    return render_template(
        "/login/login.html",
        current_user=current_user
    )

@views.route("/confirm-mobile")
def confirm_mobile():
    mobile_number = session.get("mobile_number")
    current_user = session.get("current_user")
    return render_template(
        "/confirm_mobile/confirm_mobile.html",
        mobile_number=mobile_number,
        current_user=current_user
    )

@views.route("/payment-successful")
def payment_successful():
    current_user = session.get("current_user")
    return render_template(
        "/payment_successful/payment_successful.html",
        current_user=current_user
    )

@views.route("/cart")
def cart():
    current_user_guid = session.get('current_user')
    if current_user_guid:
        current_user = User.query.filter_by(guid=current_user_guid).first()
        cart_objs = current_user.cart.books
        wishlist_objs = current_user.wishlist.books
    else:
        cart = session.get("cart") or []
        cart_objs = []
        for item in cart:
            cart_objs.append(Book.query.filter_by(guid=item).first())

        wishlist = session.get("wishlist") or []
        wishlist_objs = []
        for item in wishlist:
            wishlist_objs.append(Book.query.filter_by(guid=item).first())
    current_user = session.get("current_user")
    return render_template(
        "/cart/cart.html",
        cart = cart_objs,
        wishlist = wishlist_objs,
        current_user=current_user
    )

@views.route("/add-address")
def add_address():
    current_user = session.get("current_user")
    user = User.query.filter_by(guid=current_user).first()

    return render_template(
        "/add_address/add_address.html",
        current_user=current_user,
        user=user
    )

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