from flask import Blueprint, jsonify, make_response, request

from sqlalchemy import or_

from app.models.admin import Admin
from app.models.user import Address, User
from app.models.books import Book
from app.models.buckets import DeliveryBucket
from app.models.order import Order
from app import db

from functools import wraps

from app.api_admin.utils import validate_user, token_required

import os
import jwt
from datetime import datetime, date, timedelta

api_admin = Blueprint('api_admin', __name__, url_prefix="/api_admin")

@api_admin.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    admin = Admin.query.filter_by(username=username).first()
    if not admin:
        return jsonify({
            "status": "error",
            "message": "Invalid username"
        }), 400
    if password != admin.password:
        return jsonify({
            "status": "error",
            "message": "Incorrect password"
        }), 400
    access_token_admin = jwt.encode({'id' : admin.id, 'exp' : datetime.utcnow() + timedelta(minutes=45)}, os.environ.get('SECRET_KEY'), "HS256")
    response = make_response(jsonify({
        "status": "success",
        "admin": admin.to_json(),
    }), 200)
    response.set_cookie('access_token_admin', access_token_admin, secure=True, httponly=True, samesite='None')
    return response

@api_admin.route('/refresh')
@token_required
def refresh(admin):
    return jsonify({
        "status": "success",
        "admin": admin.to_json(),
    })

@api_admin.route('/logout', methods=['POST'])
@token_required
def logout(admin):
    response = make_response(jsonify({
        "status": "success",
    }))
    response.set_cookie('access_token_admin', '', secure=True, httponly=True, samesite='None')
    return response

@api_admin.route('/get-users')
@token_required
def get_users(admin):
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))
    search = request.args.get('query')
    sort = request.args.get('sort')

    all_users = []
    query = User.query

    if search:
        query = query.filter(or_(
                User.first_name.ilike(f'{search}%'),
                User.last_name.ilike(f'{search}%'),
                User.mobile_number.ilike(f'{search}%')
            ))
    if sort and int(sort) == 1:
        query = query.order_by(User.id)
    else:
        query = query.order_by(User.id.desc())
    all_users = query.limit(end - start).offset(start).all()
    users = []
    for user in all_users:
        user = User.query.get(user.id)
        users.append({"password": user.password, **user.to_json()})
    return jsonify({
        "status": "success",
        "users": users
    })

@api_admin.route('/update-user', methods=['POST'])
@token_required
@validate_user
def update_user(admin):
    id = request.json.get('id')
    name = request.json.get('name')
    mobile_number = request.json.get('mobile_number')
    contact_number = request.json.get('contact_number')
    address = request.json.get('address')
    pin_code = request.json.get('pin_code')
    plan_date = request.json.get('plan_date')
    plan_duration = request.json.get('plan_duration')
    plan_id = request.json.get('plan_id')
    payment_status = request.json.get('payment_status')
    source = request.json.get('source')

    if not id:
        return jsonify({
            "status": "error",
            "message": "Provide user ID"
        }), 400

    user = User.query.get(id)
    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400

    if name:
        user.first_name = name.split()[0]
        if len(name.split()) > 1:
            user.last_name = ' '.join(name.split()[1:])

    if mobile_number:
        user.mobile_number = mobile_number

    if contact_number:
        user.contact_number = contact_number

    if plan_date:
        user.plan_date = datetime.strptime(plan_date, '%Y-%m-%d')
    else:
        user.plan_date = None

    if plan_duration:
        user.plan_duration = plan_duration

    if source:
        user.source = source

    if plan_id:
        plan_id = int(plan_id)
    if plan_id == 1:
        user.plan_id = os.environ.get('RZP_PLAN_1_ID')
        user.books_per_week = 1
    elif plan_id == 2:
        user.plan_id = os.environ.get('RZP_PLAN_2_ID')
        user.books_per_week = 2
    elif plan_id == 4:
        user.plan_id = os.environ.get('RZP_PLAN_3_ID')
        user.books_per_week = 4

    if payment_status:
        user.payment_status = payment_status

    if address and pin_code:
        for user_address in user.address:
            user_address.delete()
        address = Address.create({"area": address, "pin_code": pin_code}, user.id)

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "User updated",
        "user": user.to_json()
    })

@api_admin.route('/add-user', methods=['POST'])
@token_required
@validate_user
def add_user(admin):
    name = request.json.get('name')
    mobile_number = request.json.get('mobile_number')
    password = request.json.get('password')
    contact_number = request.json.get('contact_number')
    address = request.json.get('address')
    pin_code = request.json.get('pin_code')
    plan_id = request.json.get('plan_id')
    payment_id = request.json.get('payment_id')
    plan_date = request.json.get('plan_date')
    plan_duration = request.json.get('plan_duration')
    source = request.json.get('source')
    payment_status = request.json.get('payment_status')
    current_books = request.json.get('current_books')
    next_books = request.json.get('next_books')
    if not all((name, mobile_number, password)):
        return jsonify({
            "status": "error",
            "message": "Fill all the fields"
        }), 400

    if User.query.filter_by(mobile_number=mobile_number).count():
        return jsonify({
            "status": "error",
            "message": "Mobile number already exists"
        }), 400

    first_name = name.split()[0]
    last_name = ''
    if len(name.split()) > 1:
        last_name = ' '.join(name.split()[1:])
    user = User.create(first_name, last_name, mobile_number, password)
    user.contact_number = contact_number
    user.payment_id = payment_id
    user.plan_duration = plan_duration
    user.source = source
    user.payment_status = payment_status
    if user.plan_date:
        user.plan_date = datetime.strptime(plan_date, '%Y-%m-%d')
    if plan_id:
        plan_id = int(plan_id)
    if plan_id == 1:
        user.plan_id = os.environ.get('RZP_PLAN_1_ID')
        user.books_per_week = 1
    elif plan_id == 2:
        user.plan_id = os.environ.get('RZP_PLAN_2_ID')
        user.books_per_week = 2
    elif plan_id == 4:
        user.plan_id = os.environ.get('RZP_PLAN_3_ID')
        user.books_per_week = 4

    if address and pin_code:
        address = Address.create({"area": address, "pin_code": pin_code}, user.id)

    bucket_size = 1
    if plan_id == os.environ.get('RZP_PLAN_2_ID'):
        bucket_size = 2
    elif plan_id == os.environ.get('RZP_PLAN_3_ID'):
        bucket_size = 4

    if len(current_books):
        user.last_delivery_date = date.today()

    for i in range(bucket_size):
        if i >= len(current_books):
            break
        book = Book.query.filter_by(isbn=current_books[i]).first()
        Order.create(user.id, book.id, None, user.last_delivery_date)

    for i in range(bucket_size):
        if i >= len(next_books):
            break
        book = Book.query.filter_by(isbn=current_books[i]).first()
        DeliveryBucket.create(user.id, book.id, None, None)

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "User updated",
        "user": user.to_json()
    })
