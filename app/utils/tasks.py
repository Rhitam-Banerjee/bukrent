from flask import jsonify
from app import db
from app.models.order import Order
from sqlalchemy import cast, Date
from app.models.user import User
from datetime import timedelta

def complete_all_orders(): 
    pass
    # users = db.session.query(User).join(Order).filter(
    #     cast(Order.placed_on, Date) == cast(User.next_delivery_date, Date),
    #     Order.is_completed == True
    # ).all()
    # for user in users: 
    #     user.last_delivery_date = user.next_delivery_date
    #     user.next_delivery_date = user.next_delivery_date + timedelta(days=7)
    #     user.delivery_order = 0
    # db.session.commit()
    # return jsonify({"status": "success"})