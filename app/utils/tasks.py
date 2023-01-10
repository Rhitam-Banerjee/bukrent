from app import db
from app.models.order import Order
from sqlalchemy import cast, Date
from app.models.user import User
from datetime import date, timedelta

def complete_all_orders(): 
    print('completing all orders')
    #users = db.session.query(User).join(Order).filter(
    #    cast(Order.placed_on, Date) == cast(User.next_delivery_date, Date),
    #    Order.is_completed == True,
    #    User.next_delivery_date <= date.today() - timedelta(days=2),
    #).all()
    #for user in users: 
    #    print(f'Completing order of {user.first_name} {user.last_name}')
    #    user.last_delivery_date = user.next_delivery_date
    #    user.next_delivery_date = user.next_delivery_date + timedelta(days=7)
    #    user.delivery_order = 0
    #db.session.commit()
