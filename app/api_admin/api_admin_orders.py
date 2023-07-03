from flask import jsonify, request
from sqlalchemy import cast, Date

from app.models.user import User, Child
from app.models.books import Book
from app.models.buckets import DeliveryBucket, Suggestion
from app.models.order import Order

from app import db

from app.api_admin.utils import api_admin, token_required, super_admin

from datetime import datetime, timedelta


@api_admin.route('/add-books-user', methods=['POST'])
@token_required
@super_admin
def add_books_user(admin):
    user_id = request.json.get('user_id')
    isbn_list = request.json.get('isbn_list')
    books_type = request.json.get('type')

    if not all((user_id, isbn_list)) or type(isbn_list) != type([]):
        return jsonify({
            "status": "error",
            "message": "Provide user ID and a list of ISBNs"
        }), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400

    books_found, books_not_found = [], []
    books_not_in_stock, books_not_available = [], []
    children = Child.query.filter_by(user_id=user_id).all()
    for isbn in isbn_list:
        book = Book.query.filter_by(isbn=isbn).first()
        if not book:
            books_not_found.append(isbn)
        elif not book.stock_available:
            if book.rentals:
                books_not_available.append(isbn)
            else:
                books_not_in_stock.append(isbn)
        else:
            books_found.append(isbn)
            if books_type == 'suggestions':
                for child in children:
                    Suggestion.create(user.id, book.id)
            elif books_type == 'wishlist':
                user.add_to_wishlist(book.isbn)
            elif books_type == 'previous':
                Order.create(user.id, book.id, 0,
                             datetime.now() - timedelta(days=90))
            elif books_type == 'bucket':
                DeliveryBucket.create(
                    user_id, book.id, user.next_delivery_date, 0)
            elif books_type == 'current':
                if not user.last_delivery_date:
                    user.last_delivery_date = datetime.now() - timedelta(days=7)
                    db.session.commit()
                Order.create(user.id, book.id, 0, user.last_delivery_date)
            elif books_type == 'delivery':
                if not user.next_delivery_date:
                    return jsonify({
                        "status": "error",
                        "message": "No delivery date set"
                    }), 400
                Order.create(user.id, book.id, 0, user.next_delivery_date)
                book.stock_available -= 1
                book.rentals += 1

    return jsonify({
        "status": "success",
        "books_found": books_found,
        "books_not_found": books_not_found,
        "books_not_in_stock": books_not_in_stock,
        "books_not_available": books_not_available,
        "user": admin.get_users([user])[0]
    })


@api_admin.route('/add-to-wishlist', methods=['POST'])
@token_required
@super_admin
def add_to_wishlist(admin):
    guid = request.json.get('book_guid')
    user_id = request.json.get('user_id')
    isbn = request.json.get('isbn')
    user = User.query.get(user_id)
    isbn = request.json.get("isbn")
    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    user.add_to_wishlist(isbn)
    return jsonify({
        "status": "success",
        "user": admin.get_users([user])[0]
    })


@api_admin.route('/remove-from-wishlist', methods=['POST'])
@token_required
@super_admin
def remove_from_wishlist(admin):
    guid = request.json.get('book_guid')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    user.wishlist_remove(guid)
    book = Book.query.filter_by(guid=guid).first()
    return jsonify({
        "status": "success",
        "user": admin.get_users([user])[0],
        "book": admin.get_books([book])[0],
    })


@api_admin.route('/remove-from-suggestions', methods=['POST'])
@token_required
@super_admin
def remove_from_suggestions(admin):
    user_id = request.json.get('user_id')
    book_guid = request.json.get("book_guid")
    isbn = request.json.get("isbn")
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    user.suggestion_to_dump(book_guid, isbn)
    book = Book.query.filter_by(isbn=isbn).first()
    return jsonify({
        "status": "success",
        "user": admin.get_users([user])[0],
        "book": admin.get_books([book])[0],
    })


@api_admin.route('/remove-from-previous', methods=['POST'])
@token_required
@super_admin
def remove_from_previous(admin):
    isbn = request.json.get('isbn')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    user.remove_from_previous(isbn)
    return jsonify({
        "status": "success",
        "user": admin.get_users([user])[0]
    })


@api_admin.route('/remove-from-bucket', methods=['POST'])
@token_required
@super_admin
def remove_from_bucket(admin):
    book_guid = request.json.get('book_guid')
    user_id = request.json.get('user_id')
    isbn = request.json.get('isbn')
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    user.bucket_remove(isbn)
    return jsonify({
        "status": "success",
        "user": admin.get_users([user])[0]
    })


@api_admin.route('/remove-from-delivery', methods=['POST'])
@token_required
@super_admin
def remove_from_delivery(admin):
    guid = request.json.get('book_guid')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    book = Book.query.filter_by(guid=guid).first()
    if not book:
        return jsonify({
            "status": "error",
            "message": "Invalid book ID"
        })
    delivery = Order.query.filter_by(user_id=user_id, book_id=book.id).first()
    if not delivery:
        return jsonify({
            "status": "error",
            "message": "No delivery found"
        })
    book.stock_available += 1
    book.rentals -= 1
    delivery.delete()
    db.session.commit()
    return jsonify({
        "status": "success",
        "user": admin.get_users([user])[0]
    })


@api_admin.route('/add-users-book', methods=['POST'])
@token_required
@super_admin
def add_users_book(admin):

    book_isbns = request.json.get('isbn')
    mobile_number_list = request.json.get('mobile_number_list')
    book_type = request.json.get('type')

    def user_error(message, code=400):
        return jsonify({
            "status": "error",
            "message": message
        }), code
    if book_type not in ('suggestions', 'wishlist', 'previous'):
        return user_error("Provide a valid book type")
    if not isinstance(mobile_number_list, list) or not mobile_number_list or not book_isbns:
        return user_error("Provide book ID and a list of mobile numbers")
    if not isinstance(book_isbns, list):
        book_isbns = [book_isbns]

    users_found, users_not_found = [], []
    for mobile_number in mobile_number_list:
        user = User.query.filter_by(mobile_number=mobile_number).first()
        if not user:
            users_not_found.append(mobile_number)
        else:
            users_found.append(user)
    if not users_found:
        return user_error("None of the phone numbers provided are valid")

    for book in Book.query.filter(Book.isbn.in_(book_isbns)).all():
        for user in users_found:
            if book_type == 'suggestions':
                for child in Child.query.filter_by(user_id=user.id).all():

                    Suggestion.create(user.id, book.id)
            elif book_type == 'wishlist':
                user.add_to_wishlist(book.isbn)
            elif book_type == 'previous':
                Order.create(user.id, book.id, 0,
                             datetime.now() - timedelta(days=90))
    users_found = [user.mobile_number for user in users_found]
    return jsonify({
        "status": "success",
        "users_found": users_found,
        "users_not_found": users_not_found,
        "book": admin.get_books([book])[0]
    })


@api_admin.route('/add-to-bucket', methods=['POST'])
@token_required
@super_admin
def add_to_bucket(admin):
    user_id = request.json.get('user_id')
    isbn = request.json.get('isbn')
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    book = Book.query.filter_by(isbn=isbn).first()
    if not book:
        return jsonify({
            "status": "error",
            "message": "Invalid book ID"
        }), 400
    user.wishlist_remove(isbn)
    DeliveryBucket.create(user_id, book.id, user.next_delivery_date, 0)
    return jsonify({
        "status": "success",
        "user": admin.get_users([user])[0],
        "message": "Added to bucket"
    })


@api_admin.route('/get-orders')
@token_required
@super_admin
def get_orders(admin):
    return jsonify({
        "status": "success",
        "orders": admin.get_orders()
    })


@api_admin.route('/confirm-order', methods=['POST'])
@token_required
@super_admin
def confirm_order(admin):
    user_id = request.json.get('id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    if user.plan_pause_date:
        return jsonify({
            "status": "error",
            "message": "Plan paused! Cannot place delivery"
        }), 400
    try:
        user.confirm_order()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    return jsonify({
        "status": "success",
        "user": admin.get_users([user])[0],
    })


@api_admin.route('/complete-order', methods=['POST'])
@token_required
@super_admin
def complete_order(admin):
    user_id = request.json.get('id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    if not user.next_delivery_date:
        return jsonify({"status": "error", "message": "No order placed"}), 400
    order_count = Order.query.filter(
        cast(Order.placed_on, Date) == cast(user.next_delivery_date, Date)
    ).count()
    if not order_count:
        return jsonify({"status": "error", "message": "No order placed"}), 400
    user.last_delivery_date = user.next_delivery_date
    user.next_delivery_date = user.next_delivery_date + timedelta(days=7)
    user.delivery_order = 0
    db.session.commit()
    return jsonify({
        "status": "success",
        "message": "Order completed",
        "user": admin.get_users([user])[0],
    })
