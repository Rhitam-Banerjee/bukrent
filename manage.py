from flask.cli import FlaskGroup
from app import create_app, db
from flask import current_app
from sqlalchemy import cast, Date
from flask_apscheduler import APScheduler

from app import db
from app.models.order import Order
from sqlalchemy import cast, Date
from app.models.user import User
from datetime import date, timedelta

from seed_4 import *
from export import *
from seed_users import *
from seed_books import seed_books
from script_order import *
from scripts.script_new_books_2 import seed_new_books
from scripts.script_new_books_description import seed_new_books_description
from scripts.script_new_books_details import seed_new_books_details
from scripts.script_25_aug import *
from scripts.script_26_aug import *
from scripts.script_30_aug import *
from scripts.script_8_sept import *
from scripts.script_23_sept import *
from scripts.script_multiple_images import seed_multiple_images

from app.models.annotations import Annotation
from app.models.author import Author
from app.models.books import Book
from app.models.category import Category
from app.models.details import Detail
from app.models.publishers import Publisher
from app.models.reviews import Review
from app.models.series import Series
from dotenv import load_dotenv

load_dotenv()

app = create_app()
app.app_context().push()

def complete_all_orders(): 
    with app.app_context(): 
        users = User.query.filter_by(payment_status='Paid').all()
        print('Completing All Orders')
        users = User.query.filter(User.next_delivery_date <= date.today() - timedelta(days=1)).all()
        for user in users: 
            orders = Order.query.filter_by(user_id=user.id).order_by(Order.placed_on.desc()).all()
            has_retained_books = DeliveryBucket.query.filter_by(user_id=user.id, is_retained=True).count()
            is_completed = False
            for order in orders: 
                if order.placed_on.date() == user.next_delivery_date and order.is_completed: 
                    is_completed = True
                    break
            if is_completed or (has_retained_books and date.today() == user.next_delivery_date): 
                print(f'Completed Order Of {user.first_name} {user.last_name}')
                user.last_delivery_date = user.next_delivery_date
                user.next_delivery_date = user.next_delivery_date + timedelta(days=7)
                user.delivery_order = 0
        db.session.commit()

def shift_deliveries(): 
    with app.app_context(): 
        print('Shifting deliveries')
        users = User.query.filter(User.next_delivery_date <= date.today() - timedelta(days=1)).filter_by(plan_pause_date=None, payment_status='Paid').all()
        for user in users: 
            orders = Order.query.filter_by(user_id=user.id).order_by(Order.placed_on.desc()).all()
            is_not_completed, has_order = False, False
            for order in orders: 
                if order.placed_on.date() == user.next_delivery_date: 
                    has_order = True
                    if not order.is_completed: 
                        is_not_completed = True
                        break
            next_delivery_date = user.next_delivery_date
            if user.first_name == 'Anuradha': 
                print(len(orders), is_not_completed)
            if not len(orders) or is_not_completed or (not has_order and user.deliverer_id):  
                print(f'Shifted Delivery Date Of {user.first_name} {user.last_name}')
                user.next_delivery_date = date.today()
                for order in orders: 
                    if order.placed_on.date() == next_delivery_date: 
                        order.placed_on = date.today()
                        order.is_taken = False
        db.session.commit()

def renew_plans(): 
    with app.app_context():  
        users = User.query.filter(User.plan_duration != None).filter_by(payment_status='Paid').all()
        for user in users: 
            user.total_delivery_count = user.plan_duration * 4
        print('Renewing plans')
        users = User.query.filter(
            User.plan_expiry_date <= date.today() - timedelta(days=1),
            User.plan_date != None,
            User.plan_duration != None,
        ).filter_by(payment_type='Autopay', plan_pause_date=None, payment_status='Paid').all()
        print(len(users))
        for user in users: 
            plan_expiry_date = user.plan_expiry_date
            while plan_expiry_date < date.today(): 
                user.plan_date = user.plan_expiry_date + timedelta(days=1)
                user.plan_expiry_date = user.plan_date + timedelta(days=user.plan_duration * 28)
                plan_expiry_date = user.plan_expiry_date
            print(f'Renewed Plan Of {user.first_name} {user.last_name}')
        db.session.commit()

def initialize_delivery_date(): 
    with app.app_context(): 
        print('Initializing delivery date')
        users = User.query.filter_by(next_delivery_date=None, payment_status='Paid', plan_pause_date=None).all()
        for user in users: 
            user.delivery_status = 'Active'
            user.next_delivery_date = date.today() + timedelta(days=3)
            print(f'Initialized Delivery Date Of {user.first_name} {user.last_name}')
        db.session.commit()

renew_plans()
complete_all_orders()
shift_deliveries()
initialize_delivery_date()
scheduler = APScheduler()
scheduler.add_job(func=complete_all_orders, trigger='interval', id='job-1', seconds=5040)
scheduler.add_job(func=shift_deliveries, trigger='interval', id='job-2', seconds=5040)
scheduler.add_job(func=renew_plans, trigger='interval', id='job-3', seconds=5040)
scheduler.add_job(func=initialize_delivery_date, trigger='interval', id='job-4', seconds=5040)
scheduler.start()

cli = FlaskGroup(create_app=create_app)

@cli.command()
def recreate_db():
    if current_app.config.get('ENV') not in ('development', 'test', 'testing'):
       print("ERROR: recreate-db only allowed in development and testing env.")
       return
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command()
def seed_db():
    seed()

@cli.command()
def export_db():
    export()

@cli.command()
def seed_users_data():
    seed_users()

@cli.command()
def seed_books_data(): 
    seed_books()

@cli.command()
def seed_new_books_data(): 
    seed_new_books()

@cli.command()
def seed_new_books_description_data(): 
    seed_new_books_description()

@cli.command()
def seed_new_books_details_data(): 
    seed_new_books_details()

@cli.command()
def seed_multiple_images_data(): 
    seed_multiple_images()

@cli.command()
def script_create_orders():
    create_orders()

@cli.command()
def script_25_aug():
    add_books()
    aug_25()
    # populate_suggestions()

@cli.command()
def script_26_aug():
    aug_26_1()

@cli.command()
def script_30_aug():
    aug_30_1()

@cli.command()
def script_8_sept():
    sept_8()

@cli.command()
def script_23_sept():
    sept_23()

if __name__ == '__main__':
    cli()


