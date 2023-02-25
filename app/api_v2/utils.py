from flask import Blueprint, request, jsonify
from functools import wraps
import jwt

from app.models.user import User

import os

api_v2 = Blueprint('api_v2', __name__, url_prefix="/api_v2")

api_v2_books = Blueprint('api_v2_books', __name__, url_prefix="/api_v2_books")

def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       access_token = request.cookies.get('access_token')
       if not access_token:
           return jsonify({'message': 'No access token'}), 401
       try:
           data = jwt.decode(access_token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
           user = User.query.filter_by(id=data['id']).first()
       except:
           return jsonify({'message': 'Invalid access token'})
       return f(user, *args, **kwargs)
   return decorator