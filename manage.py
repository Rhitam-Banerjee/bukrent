from flask.cli import FlaskGroup
from app import create_app, db
from flask import current_app

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
from scripts.script_25_aug import *
from scripts.script_26_aug import *
from scripts.script_30_aug import *
from scripts.script_8_sept import *
from scripts.script_23_sept import *

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
        print('Completing All Orders')
        users = User.query.filter(User.next_delivery_date <= date.today() - timedelta(days=2)).all()
        for user in users: 
            orders = Order.query.filter_by(user_id=user.id).order_by(Order.placed_on.desc()).all()
            is_completed = False
            for order in orders: 
                if order.placed_on == user.next_delivery_date and order.is_completed: 
                    is_completed = True
                    break
            if is_completed: 
                print(f'Compeleted Order Of {user.first_name} {user.last_name}')
                user.last_delivery_date = user.next_delivery_date
                user.next_delivery_date = user.next_delivery_date + timedelta(days=7)
                user.delivery_order = 0
        db.session.commit()
        print('Completed All Orders')

complete_all_orders()
scheduler = APScheduler()
scheduler.add_job(func=complete_all_orders, trigger='interval', id='job', seconds=86400)
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


