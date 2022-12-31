from flask import jsonify, request
from app.models.deliverer import Deliverer

from functools import wraps

import os
import jwt

def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       access_token_deliverer = request.cookies.get('access_token_deliverer')
       if not access_token_deliverer:
           return jsonify({'message': 'No access token'}), 401
       try:
           data = jwt.decode(access_token_deliverer, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
           deliverer = Deliverer.query.filter_by(id=data['id']).first()
       except:
           return jsonify({'message': 'Invalid access token'}), 401
       return f(deliverer, *args, **kwargs)
   return decorator