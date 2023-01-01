from datetime import date, timedelta, datetime
from flask import Blueprint, jsonify, request, make_response

from app.models.deliverer import Deliverer
from app.models.user import User
from app.models.order import Order

from app.api_delivery.utils import token_required

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
    sort = bool(request.args.get('sort'))

    if not str(time_filter).isnumeric(): 
        time_filter = 0
    else: 
        time_filter = int(time_filter)

    deliveries = []

    user_query = User.query.filter_by(deliverer_id=deliverer.id).filter(
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
        next_delivery_count = Order.query.filter_by(user_id=user.id).filter(
            Order.placed_on >= user.next_delivery_date - timedelta(days=1),
            Order.placed_on <= user.next_delivery_date + timedelta(days=1)
        ).count()
        if next_delivery_count: 
            deliveries.append({
                "last_delivery_count": last_delivery_count,
                "next_delivery_count": next_delivery_count,
                "user": {
                    "id": user_json['id'],
                    "first_name": user_json['first_name'],
                    "last_name": user_json['last_name'],
                    "mobile_number": user_json['mobile_number'],
                    "address": user_json['address'],
                    "delivery_time": user_json['delivery_time'],
                    "books_per_week": user_json['books_per_week'],
                    "next_delivery_date": user_json['next_delivery_date'],
                }
            })

    return jsonify({
        "status": "success",
        "deliveries": deliveries
    })