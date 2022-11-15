from flask import jsonify, request
from app.models.books import Book
from app.models.user import User
from app.models.admin import Admin

from functools import wraps

import os
import jwt
from datetime import datetime

def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       access_token = request.cookies.get('access_token')
       if not access_token:
           return jsonify({'message': 'No access token'}), 401
       try:
           data = jwt.decode(access_token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
           admin = Admin.query.filter_by(id=data['id']).first()
       except:
           return jsonify({'message': 'Invalid access token'})
       return f(admin, *args, **kwargs)
   return decorator

def validate_user(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        mobile_number = request.json.get('mobile_number')
        contact_number = request.json.get('contact_number')
        pin_code = request.json.get('pin_code')
        plan_id = request.json.get('plan_id')
        plan_duration = request.json.get('plan_duration')
        plan_date = request.json.get('plan_date')
        current_books = request.json.get('current_books')
        next_books = request.json.get('next_books')
        payment_status = request.json.get('payment_status')
        payment_id = request.json.get('payment_id')
        try:
            if mobile_number and (not mobile_number.isnumeric() or len(mobile_number) != 10):
                raise ValueError("Invalid mobile number")
            if contact_number and (not contact_number.isnumeric() or len(contact_number) != 10):
                raise ValueError("Invalid contact number")
            if pin_code and len(pin_code) != 6:
                raise ValueError("Invalid PIN code")
            if plan_id and int(plan_id) not in [1, 2, 4]:
                raise ValueError("Invalid plan ID")
            if plan_duration and int(plan_duration) not in [1, 3, 12]:
                raise ValueError("Invalid plan duration")
            if payment_status and payment_status not in ['Paid', 'Unpaid', 'Trial']:
                raise ValueError("Invalid payment status")
            if plan_date:
                _plan_date = datetime.strptime(plan_date, '%Y-%m-%d')
                if _plan_date > datetime.today():
                    raise ValueError("Invalid plan date")
            if current_books:
                for isbn in current_books:
                    if not Book.query.filter_by(isbn=isbn).count():
                        raise ValueError(f"Invalid ISBN {isbn}")
            if next_books:
                for isbn in next_books:
                    if not Book.query.filter_by(isbn=isbn).count():
                        raise ValueError(f"Invalid ISBN {isbn}")
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400
        return f(*args, **kwargs)
    return decorator
