from flask import jsonify, request

from sqlalchemy import or_

from sqlalchemy import cast, Date


from app.models.user import Address, User, Child
from app.models.books import Book
from app.models.buckets import DeliveryBucket
from app.models.order import Order
from app.models.deliverer import Deliverer
from app import db

from app.api_admin.utils import api_admin, validate_user, token_required, super_admin

import os
from datetime import datetime, date

@api_admin.route('/get-users')
@token_required
@super_admin
def get_users(admin):
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))
    search = request.args.get('query')
    sort = request.args.get('sort')
    payment_status = request.args.get('payment_status')
    plan = request.args.get('plan')
    plan_duration = request.args.get('duration')
    delivery_date = request.args.get('delivery_date')
    deliverer_id = request.args.get('deliverer_id')

    all_users = []
    query = User.query.filter_by(is_deleted=False)

    if payment_status:
        if payment_status == 'Unpaid':
            query = query.filter(or_(User.payment_status == 'Unpaid', User.payment_status == None, User.payment_status == ''))
        else:
            query = query.filter_by(payment_status=payment_status)
    if plan:
        query = query.filter_by(books_per_week=plan)
    if plan_duration:
        query = query.filter_by(plan_duration=plan_duration)
    if delivery_date: 
        delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d').date()
        query = query.filter_by(next_delivery_date=delivery_date)
    if deliverer_id: 
        query = query.filter_by(deliverer_id=deliverer_id)
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
    
    completed_delivery_count = []
    if delivery_date: 
        completed_delivery_count = query.join(Order).filter(Order.is_completed == True, Order.placed_on == delivery_date).all()
    total_users = query.count()

    return jsonify({
        "status": "success",
        "users": admin.get_users(all_users),
        "completed_delivery_count": len(completed_delivery_count),
        "total_users": total_users,
    })

@api_admin.route('/get-user/<id>')
@token_required
@super_admin
def get_user(admin, id): 
    user = User.query.filter_by(id=id).first()
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    return jsonify({
        "status": "success",
        "user": admin.get_users([user])[0]
    })

@api_admin.route('/get-archived-users')
@token_required
@super_admin
def get_archived_users(admin):
    users = User.query.filter_by(is_deleted=True).all()
    return jsonify({
        "status": "success",
        "users": [user.to_json() for user in users]
    })

@api_admin.route('/update-user', methods=['POST'])
@token_required
@super_admin
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
    password = request.json.get('password')
    children = request.json.get('children')

    if not mobile_number: 
        return jsonify({
            "status": "error",
            "message": "Mobile number is necessary"
        }), 400

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
    else: 
        user.first_name = ''
        user.last_name = ''

    user.mobile_number = mobile_number
    user.contact_number = contact_number
    user.password = password
    user.plan_duration = plan_duration
    user.source = source

    if plan_date:
        user.plan_date = datetime.strptime(plan_date, '%Y-%m-%d')
    else: 
        user.plan_date = None

    user_children = Child.query.filter_by(user_id=user.id).all()
    for child in user_children: 
        child.delete()
    if children and type(children) == type([]):
        for child in children:
            child_obj = Child.query.filter_by(user_id=user.id, name=child['name']).first()
            if not child_obj:
                user.add_child(child)

    if plan_id and plan_id.isnumeric(): 
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

    for user_address in user.address:
        user_address.delete()
    if address and pin_code:
        address = Address.create({"area": address, "pin_code": pin_code}, user.id)

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "User updated",
        "user": admin.get_users([user])[0],
    })

@api_admin.route('/update-delivery-details', methods=['POST'])
@token_required
@super_admin
def update_delivery_details(admin): 
    id = request.json.get('id')
    next_delivery_date = request.json.get('next_delivery_date')
    deliverer_id = request.json.get('deliverer_id')
    delivery_time = request.json.get('delivery_time')
    delivery_address = request.json.get('delivery_address')
    delivery_order = request.json.get('delivery_order')
    if not all((next_delivery_date, deliverer_id, delivery_time, delivery_order)): 
        return jsonify({"status": "error", "message": "Provide all the details"}), 400
        
    delivery_date = datetime.strptime(next_delivery_date, '%Y-%m-%d')
    user = User.query.get(id)
    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    if not delivery_date or delivery_date.date() < date.today() or (user.last_delivery_date and delivery_date.date() <= user.last_delivery_date):
        return jsonify({"status": "error", "message": "Invalid delivery date"}), 400
    if delivery_order is None or not str(delivery_order).isnumeric() or int(delivery_order) < 1: 
        return jsonify({"status": "error", "message": "Invalid delivery order input"}), 400
    if User.query.filter_by(
        next_delivery_date=delivery_date.date(), 
        delivery_order=delivery_order,
        deliverer_id=deliverer_id,
    ).filter(User.id != user.id).count(): 
        return jsonify({"status": "error", "message": "Provided delivery order is already marked to other delivery"}), 400

    user.next_delivery_date = delivery_date
    if not deliverer_id: 
        user.deliverer = None
    else: 
        if Deliverer.query.get(deliverer_id): 
            user.deliverer_id = deliverer_id

    user.delivery_order = delivery_order
    user.delivery_address = delivery_address
    db.session.commit()
    orders = Order.query.filter_by(user_id=user.id).filter(
        cast(Order.placed_on, Date) == cast(user.next_delivery_date, Date),
    ).all()
    for order in orders: 
        order.delivery_address = user.delivery_address

    user.delivery_time = delivery_time

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "User updated",
        "user": admin.get_users([user])[0],
    })

@api_admin.route('/update-user-ops', methods=['POST'])
@token_required
@super_admin
def update_user_ops(admin): 
    id = request.json.get('id')
    contact_number = request.json.get('contact_number')
    delivery_date = request.json.get('delivery_date')
    delivery_count = request.json.get('delivery_count')
    deliverer_id = request.json.get('deliverer_id')
    if delivery_count is None or not str(delivery_count).isnumeric() or int(delivery_count) < 0: 
        return jsonify({"status": "error", "message": "Invalid delivery count"}), 400
    user = User.query.get(id)
    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d')
    if not delivery_date or delivery_date.date() < date.today() or (user.last_delivery_date and delivery_date.date() <= user.last_delivery_date):
        return jsonify({"status": "error", "message": "Invalid delivery date"}), 400
    user.next_delivery_date = delivery_date
    user.delivery_count = delivery_count
    if contact_number and len(str(contact_number)) == 10 and str(contact_number).isnumeric(): 
        user.contact_number = contact_number
    if not deliverer_id: 
        user.deliverer_id = None
    else: 
        if Deliverer.query.get(deliverer_id): 
            user.deliverer_id = deliverer_id
    db.session.commit()
    return jsonify({
        "status": "success",
        "message": "User updated",
        "user": admin.get_users([user])[0],
    })

@api_admin.route('/add-user', methods=['POST'])
@token_required
@super_admin
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
    children = request.json.get('children')
    if not all((name, mobile_number, password)):
        return jsonify({
            "status": "error",
            "message": "Fill all the fields"
        }), 400
    if not children or not len(children):
        return jsonify({
            "status": "error",
            "message": "Add atleast 1 child"
        }), 400
    if User.query.filter_by(mobile_number=mobile_number, is_deleted=False).count():
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
    if plan_date:
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

    if children and type(children) == type([]) and len(children):
        for child in children:
            user.add_child(child)
        #age_groups = []
        #for child in children:
        #    age_groups.append(child.get("age_group"))
        #age_groups = list(set(age_groups))
        #user.add_age_groups(age_groups)

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
        "user": admin.get_users([user])[0],
    })

@api_admin.route('/delete-user', methods=['POST'])
@token_required
@super_admin
def delete_user(admin):
    id = request.json.get('id')

    user = User.query.get(id)
    if not user or user.is_deleted:
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400

    user.is_deleted = True

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "User deleted"
    })

@api_admin.route('/restore-user', methods=['POST'])
@token_required
@super_admin
def restore_user(admin):
    id = request.json.get('id')

    user = User.query.get(id)
    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400

    user.is_deleted = False

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "User restored"
    })
