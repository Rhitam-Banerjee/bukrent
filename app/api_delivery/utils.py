from datetime import date
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

def sort_deliveries(d1, d2): 
    try: 
        if d1['user']['next_delivery_date'] == d2['user']['next_delivery_date']: 
            if not d1['user']['delivery_time'] or len(d1['user']['delivery_time'].split('-')[0]) < 3: 
                return -1
            if not d2['user']['delivery_time'] or len(d2['user']['delivery_time'].split('-')[0]) < 3: 
                return 1
            d1_time, d2_time = d1['user']['delivery_time'].split('-')[0].strip(), d2['user']['delivery_time'].split('-')[0].strip()
            if d1_time[len(d1_time) - 2].lower() == d2_time[len(d2_time) - 2].lower():
                return int(d1_time[0: len(d1_time) - 2]) - int(d2_time[0: len(d2_time) - 2])
            elif d1_time[len(d1_time) - 2].lower() == 'am': 
                return 1
            else: 
                return -1
        if d1['user']['next_delivery_date'] < d2['user']['next_delivery_date']: 
            return -1
        else: 
            return 1
    except Exception as e:
        print(e)
        return -1 