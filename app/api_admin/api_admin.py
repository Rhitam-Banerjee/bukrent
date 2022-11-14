from flask import Blueprint, jsonify, make_response, request

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
    access_token = jwt.encode({'id' : admin.id, 'exp' : datetime.utcnow() + timedelta(minutes=45)}, os.environ.get('SECRET_KEY'), "HS256")
    response = make_response(jsonify({
        "status": "success",
        "admin": admin.to_json(),
    }), 200)
    response.set_cookie('access_token', access_token, secure=True, httponly=True, samesite='None')
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
    response.set_cookie('access_token', '', secure=True, httponly=True, samesite='None')
    return response

@api_admin.route('/get-users')
@token_required
def get_users(admin):
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))
    all_users = User.query.limit(end - start).offset(start).all()
    users = []
    for user in all_users:
        users.append(user.to_json())
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
    if plan_duration:
        user.plan_duration = plan_duration
    if plan_id:
        user.plan_id = plan_id
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
    if not all((name, mobile_number, address, pin_code, plan_id, plan_date, plan_duration, payment_status)):
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
    user = User.create(first_name, last_name, mobile_number, '')
    user.contact_number = contact_number
    user.plan_id = plan_id
    user.payment_id = payment_id
    user.plan_date = datetime.strptime(plan_date, '%Y-%m-%d')
    user.plan_duration = plan_duration
    user.source = source
    user.payment_status = payment_status
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
