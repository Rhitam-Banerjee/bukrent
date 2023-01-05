from flask import jsonify, request

from app.models.user import User, Child
from app.models.books import Book
from app.models.buckets import DeliveryBucket, Suggestion
from app.models.order import Order

from app import db

from app.api_admin.utils import api_admin, token_required

from datetime import datetime, timedelta

@api_admin.route('/add-books-user', methods=['POST'])
@token_required
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
    children = Child.query.filter_by(user_id=user_id).all()
    for isbn in isbn_list: 
        book = Book.query.filter_by(isbn=isbn).first()
        if not book: 
            books_not_found.append(isbn)
        else: 
            books_found.append(isbn)
            if books_type == 'suggestions': 
                for child in children: 
                    Suggestion.create(user.id, book.id, child.age_group)
            elif books_type == 'wishlist': 
                user.add_to_wishlist(book.guid)
            elif books_type == 'previous': 
                Order.create(user.id, book.id, 0, datetime.now() - timedelta(days=90))
            elif books_type == 'bucket': 
                DeliveryBucket.create(user_id, book.id, user.next_delivery_date, 0)
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

    return jsonify({
        "status": "success",
        "books_found": books_found,
        "books_not_found": books_not_found,
        "user": admin.get_users([user])[0]
    })

@api_admin.route('/add-to-wishlist', methods=['POST'])
@token_required
def add_to_wishlist(admin): 
    book_guid = request.json.get('book_guid')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    user.add_to_wishlist(book_guid)
    return jsonify({
        "status": "success",
        "user": admin.get_users([user])[0]
    })

@api_admin.route('/remove-from-wishlist', methods=['POST'])
@token_required
def remove_from_wishlist(admin): 
    book_guid = request.json.get('book_guid')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    user.wishlist_remove(book_guid)
    book = Book.query.filter_by(guid=book_guid).first()
    return jsonify({
        "status": "success",
        "user": admin.get_users([user])[0],
        "book": admin.get_books([book])[0],
    })

@api_admin.route('/remove-from-suggestions', methods=['POST'])
@token_required
def remove_from_suggestions(admin): 
    book_guid = request.json.get('book_guid')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    user.suggestion_to_dump(book_guid)
    book = Book.query.filter_by(guid=book_guid).first()
    return jsonify({
        "status": "success",
        "user": admin.get_users([user])[0],
        "book": admin.get_books([book])[0],
    })

@api_admin.route('/remove-from-previous', methods=['POST'])
@token_required
def remove_from_previous(admin): 
    book_guid = request.json.get('book_guid')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    user.remove_from_previous(book_guid)
    return jsonify({
        "status": "success",
        "user": admin.get_users([user])[0]
    })

@api_admin.route('/remove-from-bucket', methods=['POST'])
@token_required
def remove_from_bucket(admin): 
    book_guid = request.json.get('book_guid')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    user.bucket_remove(book_guid)
    return jsonify({
        "status": "success",
        "user": admin.get_users([user])[0]
    })

@api_admin.route('/remove-from-delivery', methods=['POST'])
@token_required
def remove_from_delivery(admin): 
    book_guid = request.json.get('book_guid')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    book = Book.query.filter_by(guid=book_guid).first()
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
    delivery.delete()
    return jsonify({
        "status": "success",
        "user": admin.get_users([user])[0]
    })

@api_admin.route('/add-users-book', methods=['POST'])
@token_required
def add_users_book(admin): 
    book_guid = request.json.get('book_guid')
    mobile_number_list = request.json.get('mobile_number_list')
    book_type = request.json.get('type')

    if not all((book_guid, mobile_number_list)) or type(mobile_number_list) != type([]): 
        return jsonify({
            "status": "error",
            "message": "Provide book ID and a list of mobile numbers"
        }), 400
    book = Book.query.filter_by(guid=book_guid).first()
    if not book: 
        return jsonify({
            "status": "error",
            "message": "Invalid book ID"
        }), 400
    
    users_found, users_not_found = [], []
    for mobile_number in mobile_number_list: 
        user = User.query.filter_by(mobile_number=mobile_number).first()
        if not user: 
            users_not_found.append(mobile_number)
        else: 
            children = Child.query.filter_by(user_id=user.id).all()
            users_found.append(mobile_number)
            if book_type == 'suggestions': 
                for child in children: 
                    Suggestion.create(user.id, book.id, child.age_group)
            elif book_type == 'wishlist': 
                user.add_to_wishlist(book.guid)
            elif book_type == 'previous': 
                Order.create(user.id, book.id, 0, datetime.now() - timedelta(days = 90))

    return jsonify({
        "status": "success",
        "users_found": users_found,
        "users_not_found": users_not_found,
        "book": admin.get_books([book])[0]
    })

@api_admin.route('/add-to-bucket', methods=['POST'])
@token_required
def add_to_bucket(admin): 
    user_id = request.json.get('user_id')
    book_guid = request.json.get('book_guid')
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    book = Book.query.filter_by(guid=book_guid).first()
    if not book: 
        return jsonify({
            "status": "error",
            "message": "Invalid book ID"
        }), 400
    user.wishlist_remove(book_guid)
    DeliveryBucket.create(user_id, book.id, user.next_delivery_date, 0)
    return jsonify({
        "status": "success",
        "user": admin.get_users([user])[0],
        "message": "Added to bucket"
    })

@api_admin.route('/get-orders')
@token_required
def get_orders(admin): 
    return jsonify({
        "status": "success",
        "orders": admin.get_orders()
    })

@api_admin.route('/confirm-order', methods=['POST'])
@token_required
def confirm_order(admin): 
    user_id = request.json.get('id')
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
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
        Order.placed_on >= user.next_delivery_date - timedelta(days=1),
        Order.placed_on <= user.next_delivery_date + timedelta(days=1)
    ).count()
    if not order_count: 
        return jsonify({"status": "error", "message": "No order placed"}), 400
    user.last_delivery_date = user.next_delivery_date
    user.next_delivery_date = user.next_delivery_date + timedelta(days=7)
    db.session.commit()
    return jsonify({
        "status": "success",
        "message": "Order completed",
        "user": admin.get_users([user])[0],
    })
