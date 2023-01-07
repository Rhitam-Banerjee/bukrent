from datetime import date, datetime, timedelta
from functools import cmp_to_key
from flask import Blueprint, jsonify, request, make_response
from sqlalchemy import or_

from app.models.deliverer import Deliverer
from app.models.user import User
from app.models.buckets import DeliveryBucket
from app.models.order import Order
from app.models.books import Book

from app.api_delivery.utils import sort_deliveries, token_required

from app import db

import os
import jwt

api_delivery = Blueprint('api_delivery', __name__, url_prefix="/api_delivery")

@api_delivery.route('/get-deliverers')
def get_deliverers(): 
    deliverers = Deliverer.query.all()
    return jsonify({
        "status": "success",
        "deliverers": [deliverer.to_json() for deliverer in deliverers]
    })

@api_delivery.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    deliverer = Deliverer.query.filter_by(username=username).first()
    if not deliverer:
        return jsonify({
            "status": "error",
            "message": "Invalid username"
        }), 400
    if password != deliverer.password:
        return jsonify({
            "status": "error",
            "message": "Incorrect password"
        }), 400
    access_token_deliverer = jwt.encode({'id' : deliverer.id}, os.environ.get('SECRET_KEY'), "HS256")
    response = make_response(jsonify({
        "status": "success",
        "deliverer": deliverer.to_json(),
    }), 200)
    response.set_cookie('access_token_deliverer', access_token_deliverer, secure=True, httponly=True, samesite='None')
    return response

@api_delivery.route('/refresh')
@token_required
def refresh(deliverer):
    return jsonify({
        "status": "success",
        "deliverer": deliverer.to_json(),
    })

@api_delivery.route('/logout', methods=['POST'])
@token_required
def logout(deliverer):
    response = make_response(jsonify({
        "status": "success",
    }))
    response.set_cookie('access_token_deliverer', '', secure=True, httponly=True, samesite='None')
    return response

@api_delivery.route('/get-deliveries')
@token_required
def get_deliveries(deliverer): 
    time_filter = request.args.get('time_filter')
    sort = request.args.get('sort')
    search_query = request.args.get('search_query')

    if not str(time_filter).strip('-').isnumeric(): 
        time_filter = 0
    else: 
        time_filter = int(time_filter)

    if not str(sort).isnumeric(): 
        sort = False
    else: 
        sort = bool(int(sort))

    deliveries = []

    user_query = User.query.filter_by(deliverer_id=deliverer.id).filter(
        or_(
            User.first_name.ilike(f'{search_query}%'),
            User.last_name.ilike(f'{search_query}%'),
            User.mobile_number.ilike(f'{search_query}%')
        )
    )
    if time_filter == 1: 
        user_query = user_query.filter(User.next_delivery_date == date.today() + timedelta(days=1))
    elif time_filter == -1: 
        user_query = user_query.filter(User.next_delivery_date == date.today() - timedelta(days=1))
    else: 
        user_query = user_query.filter(
            User.next_delivery_date >= date.today(),
            User.next_delivery_date <= date.today() + timedelta(days=time_filter)
        )
    if sort: 
        user_query = user_query.order_by(User.next_delivery_date)
    else: 
        user_query = user_query.order_by(User.next_delivery_date.desc())

    users = user_query.all()
    
    for user in users: 
        user_json = user.to_json()
        last_delivery_count = 0
        if user.last_delivery_date: 
            last_delivery_count = Order.query.filter_by(user_id=user.id).filter(
                Order.placed_on >= user.last_delivery_date - timedelta(days=1),
                Order.placed_on <= user.last_delivery_date + timedelta(days=1)
            ).count()
            last_delivery_count -= DeliveryBucket.query.filter_by(
                user_id=user.id, 
                delivery_date=user.last_delivery_date
            ).count()
        total_delivery_query = Order.query.filter_by(user_id=user.id).filter(
            Order.placed_on >= user.next_delivery_date - timedelta(days=1),
            Order.placed_on <= user.next_delivery_date + timedelta(days=1)
        )
        next_delivery_count = total_delivery_query.count()
        next_delivery_refused_count = total_delivery_query.filter_by(is_refused=True).count()
        if next_delivery_count: 
            next_order = Order.query.filter_by(user_id=user.id).filter(
                Order.placed_on >= user.next_delivery_date - timedelta(days=1),
                Order.placed_on <= user.next_delivery_date + timedelta(days=1)
            ).first()
            delivery_address = ""
            if next_order.delivery_address: 
                delivery_address = next_order.delivery_address
            if user.delivery_address: 
                delivery_address = user.delivery_address
            deliveries.append({
                "last_delivery_count": last_delivery_count,
                "next_delivery_count": next_delivery_count - next_delivery_refused_count,
                "delivery_address": delivery_address,
                "is_completed": next_order.is_completed,
                "user": {
                    "id": user_json['id'],
                    "first_name": user_json['first_name'],
                    "last_name": user_json['last_name'],
                    "mobile_number": user_json['mobile_number'],
                    "address": user_json['address'],
                    "delivery_time": user_json['delivery_time'],
                    "books_per_week": user_json['books_per_week'],
                    "next_delivery_date": user_json['next_delivery_date'],
                    "delivery_order": user_json['delivery_order'],
                }
            })

    if sort: 
        deliveries = sorted(deliveries, key=cmp_to_key(sort_deliveries), reverse=False)
    else: 
        deliveries = sorted(deliveries, key=cmp_to_key(sort_deliveries), reverse=True)

    return jsonify({
        "status": "success",
        "deliveries": deliveries
    })

@api_delivery.route('/get-delivery/<id>')
@token_required
def get_delivery(deliverer, id): 
    user = User.query.get(id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID",
        }), 400
    delivery_books, return_books, delivery_address = [], [], ""
    if user.next_delivery_date: 
        delivery_books = Order.query.filter_by(user_id=user.id).filter(
            Order.placed_on >= user.next_delivery_date - timedelta(days=1),
            Order.placed_on <= user.next_delivery_date + timedelta(days=1)
        ).all()
    if not len(delivery_books): 
        return jsonify({
            "status": "error",
            "message": "No delivery scheduled for the user",
        }), 400
    if delivery_books[0].delivery_address: 
        delivery_address = delivery_books[0].delivery_address
    if user.delivery_address: 
        delivery_address = user.delivery_address
    if user.last_delivery_date: 
        return_books = Order.query.filter_by(user_id=user.id).filter(
            Order.placed_on >= user.last_delivery_date - timedelta(days=1),
            Order.placed_on <= user.last_delivery_date + timedelta(days=1)
        ).all()
    user_json = user.to_json()
    return jsonify({
        "status": "success",
        "delivery": {
            "wishlist": user.get_wishlist(),
            "suggestions": user.get_suggestions(),
            "delivery_books": [delivery_book.to_json() for delivery_book in delivery_books],
            "return_books": [return_book.to_json() for return_book in return_books],
            "notes": delivery_books[0].notes,
            "received_by": delivery_books[0].received_by,
            "is_completed": delivery_books[0].is_completed,
            "delivery_address": delivery_address,
            "user": {
                "id": user_json['id'],
                "first_name": user_json['first_name'],
                "last_name": user_json['last_name'],
                "mobile_number": user_json['mobile_number'],
                "address": user_json['address'],
                "books_per_week": user_json['books_per_week'],
            }
        }
    })

@api_delivery.route('/confirm-delivery/<id>', methods=['POST'])
@token_required
def confirm_delivery(deliverer, id): 
    received_by = request.json.get('received_by')
    notes = request.json.get('notes')
    user = User.query.get(id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID",
        }), 400
    if not user.next_delivery_date: 
        return jsonify({
            "status": "error",
            "message": "No delivery scheduled for the user",
        }), 400
    current_orders = Order.query.filter_by(user_id=user.id).filter(
        Order.placed_on >= user.next_delivery_date - timedelta(days=1),
        Order.placed_on <= user.next_delivery_date + timedelta(days=1)
    ).all()
    if not len(current_orders): 
        return jsonify({
            "status": "error",
            "message": "No delivery scheduled for the user",
        }), 400
    if user.next_delivery_date < date.today(): 
        return jsonify({
            "status": "error",
            "message": "Delivery is not scheduled for today",
        }), 400
    for order in current_orders: 
        if not order.is_completed: 
            order.delivery_time = datetime.now()
        order.received_by = received_by
        order.notes = notes
        order.is_completed = True
    # user.last_delivery_date = user.next_delivery_date
    # user.next_delivery_date = user.next_delivery_date + timedelta(days=7)
    # user.delivery_order = 0
    db.session.commit()
    return jsonify({"status": "success"})

@api_delivery.route('/toggle-refuse-book', methods=['POST'])
@token_required
def toggle_refuse_book(deliverer): 
    book_id = request.json.get('book_id')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID",
        }), 400
    if not user.next_delivery_date or date.today() < user.next_delivery_date: 
        return jsonify({
            "status": "error",
            "message": "No delivery scheduled for the user",
        }), 400
    order = Order.query.filter_by(user_id=user.id, book_id=book_id).filter(
        Order.placed_on >= user.next_delivery_date - timedelta(days=1),
        Order.placed_on <= user.next_delivery_date + timedelta(days=1)
    ).first()
    if not order: 
        return jsonify({
            "status": "error",
            "message": "Book not in delivery bucket",
        }), 400
    if order.is_refused: 
        order.is_refused = False
    else: 
        order.is_refused = True
    db.session.commit()
    return jsonify({"status": "success"})

@api_delivery.route('/toggle-retain-book', methods=['POST'])
@token_required
def toggle_retain_book(deliverer): 
    book_id = request.json.get('book_id')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID",
        }), 400
    if not user.next_delivery_date or date.today() < user.next_delivery_date: 
        return jsonify({
            "status": "error",
            "message": "No delivery scheduled for the user",
        }), 400
    order = Order.query.filter_by(user_id=user.id, book_id=book_id).filter(
        Order.placed_on >= user.last_delivery_date - timedelta(days=1),
        Order.placed_on <= user.last_delivery_date + timedelta(days=1)
    ).first()
    if not order: 
        return jsonify({
            "status": "error",
            "message": "Book not in delivery bucket",
        }), 400
    bucket_book = DeliveryBucket.query.filter_by(user_id=user.id, book_id=book_id).first()
    if not bucket_book: 
        DeliveryBucket.create(user_id, book_id, user.last_delivery_date, 0, True)
    else: 
        db.session.delete(bucket_book)
    db.session.commit()
    return jsonify({"status": "success"})

@api_delivery.route('/add-to-delivery', methods=['POST'])
@token_required
def add_to_delivery(deliverer): 
    isbn = request.json.get('isbn')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID",
        }), 400
    if not user.next_delivery_date or date.today() < user.next_delivery_date: 
        return jsonify({
            "status": "error",
            "message": "No delivery scheduled for the user",
        }), 400
    book = Book.query.filter_by(isbn=isbn).first()
    if not book: 
        return jsonify({
            "status": "error",
            "message": "Invalid ISBN",
        }), 400
    Order.create(user_id, book.id, 0, user.next_delivery_date)
    return jsonify({"status": "success"})

@api_delivery.route('/remove-from-delivery', methods=['POST'])
@token_required
def remove_from_delivery(deliverer): 
    book_id = request.json.get('book_id')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID",
        }), 400
    if not user.next_delivery_date or date.today() < user.next_delivery_date: 
        return jsonify({
            "status": "error",
            "message": "No delivery scheduled for the user",
        }), 400
    book = Book.query.get(book_id)
    if not book: 
        return jsonify({
            "status": "error",
            "message": "Invalid book ID",
        }), 400
    order = Order.query.filter_by(user_id=user_id, book_id=book.id).filter(
        Order.placed_on >= user.next_delivery_date - timedelta(days=1),
        Order.placed_on <= user.next_delivery_date + timedelta(days=1)
    ).first()
    if not order: 
        return jsonify({
            "status": "error",
            "message": "No delivery found",
        }), 400
    order.delete()
    return jsonify({"status": "success"})

@api_delivery.route('/add-to-previous', methods=['POST'])
@token_required
def add_to_previous(deliverer): 
    isbn = request.json.get('isbn')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID",
        }), 400
    book = Book.query.filter_by(isbn=isbn).first()
    if not book: 
        return jsonify({
            "status": "error",
            "message": "Invalid ISBN",
        }), 400
    if not user.last_delivery_date: 
        user.last_delivery_date = user.next_delivery_date - timedelta(days=7)
        db.session.commit()
    Order.create(user_id, book.id, 0, user.last_delivery_date)
    return jsonify({"status": "success"})

@api_delivery.route('/remove-from-previous', methods=['POST'])
@token_required
def remove_from_previous(deliverer): 
    book_id = request.json.get('book_id')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID",
        }), 400
    if not user.last_delivery_date: 
        return jsonify({
            "status": "error",
            "message": "No delivery found",
        }), 400
    book = Book.query.get(book_id)
    if not book: 
        return jsonify({
            "status": "error",
            "message": "Invalid book ID",
        }), 400
    order = Order.query.filter_by(user_id=user_id, book_id=book.id).filter(
        Order.placed_on >= user.last_delivery_date - timedelta(days=1),
        Order.placed_on <= user.last_delivery_date + timedelta(days=1)
    ).first()
    if not order: 
        return jsonify({
            "status": "error",
            "message": "No delivery found",
        }), 400
    order.delete()
    return jsonify({"status": "success"})