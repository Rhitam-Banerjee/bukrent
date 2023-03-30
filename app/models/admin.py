from datetime import timedelta
from sqlalchemy import Date, cast
from sqlalchemy.orm import load_only
from app import db
from app.models.user import User
from app.models.buckets import DeliveryBucket, Suggestion, Wishlist, Dump
from app.models.order import Order
from app.models.category import Category

class Admin(db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    is_super_admin = db.Column(db.Boolean, default=False)
    password = db.Column(db.String, nullable=False)

    def get_books(self, books, fetch_user_data=False): 
        final_books = []
        for book in books:
            tags = []
            book_json = book.to_json()
            for tag in book_json['categories']:
                tag_obj = Category.query.filter_by(name=tag).first()
                tags.append({"guid": tag_obj.guid, "name": tag_obj.name})
            book_json['tags'] = tags
            if fetch_user_data: 
                fields = ['user_id']
                suggestions = Suggestion.query.filter_by(book_id=book.id).options(load_only(*fields)).all()
                wishlists = Wishlist.query.filter_by(book_id=book.id).options(load_only(*fields)).all()
                dumps = Dump.query.filter_by(book_id=book.id, read_before=True).options(load_only(*fields)).all()
                orders = Order.query.filter_by(book_id=book.id).options(load_only(*fields)).all()
                suggested_users, wishlisted_users, previous_users = [], [], []
                for suggestion in suggestions: 
                    user = User.query.get(suggestion.user_id)
                    if user: 
                        suggested_users.append(user.to_json())
                for wishlist in wishlists: 
                    user = User.query.get(wishlist.user_id)
                    if user: 
                        wishlisted_users.append(user.to_json())
                for dump in dumps: 
                    user = User.query.get(dump.user_id)
                    if user: 
                        previous_users.append(user.to_json())
                for order in orders: 
                    user = User.query.get(order.user_id)
                    if user: 
                        previous_users.append(user.to_json())
                book_json['suggested_users'] = suggested_users
                book_json['wishlisted_users'] = wishlisted_users
                book_json['previous_users'] = previous_users
            final_books.append(book_json)
        return final_books

    def get_users(self, users): 
        all_users = []
        for user in users: 
            user_id = ''
            if type(user) == type({}): 
                user_id = user['id']
                user = User.query.get(user_id)
            current_books, delivery_books, delivery_address, notes, is_completed = [], [], "", "", False
            if user.next_delivery_date: 
                delivery_books = Order.query.filter_by(user_id=user.id).filter(
                    Order.placed_on >= user.next_delivery_date - timedelta(days=1),
                    Order.placed_on <= user.next_delivery_date + timedelta(days=1)
                ).all()
                if len(delivery_books): 
                    delivery_address = delivery_books[0].delivery_address
                    notes = delivery_books[0].notes
                    is_completed = delivery_books[0].is_completed
                if user.delivery_address: 
                    delivery_address = user.delivery_address
            if user.last_delivery_date: 
                current_books = Order.query.filter_by(user_id=user.id).filter(
                    Order.placed_on >= user.last_delivery_date - timedelta(days=1),
                    Order.placed_on <= user.last_delivery_date + timedelta(days=1)
                ).all()
            retained_books = DeliveryBucket.query.filter_by(user_id=user.id, is_retained=True).all()
            bucket = user.get_next_bucket()
            plan_expiry_date = None
            if user.plan_date and user.plan_duration:
                plan_expiry_date = user.plan_date + timedelta(days=user.plan_duration * 28)
            all_users.append({
                "plan_expiry_date": plan_expiry_date,
                "password": user.password,
                "wishlist": user.get_wishlist(),
                "suggestions": user.get_suggestions(),
                "previous": user.get_previous_books(),
                "order": {
                    "current_books": [order.to_json() for order in [*current_books, *retained_books]],
                    "delivery_books": [order.to_json() for order in delivery_books],
                    "bucket": bucket,
                    "delivery_address": delivery_address,
                    "notes": notes,
                    "is_completed": is_completed,
                },
                **user.to_json()
            })
        return all_users

    def get_orders(self): 
        users = User.query.filter(User.next_delivery_date != None).all()
        orders = []
        for user in users: 
            current_books, delivery_books = [], []
            if user.next_delivery_date: 
                delivery_books = Order.query.filter_by(user_id=user.id).filter(
                    cast(Order.placed_on, Date) == cast(user.next_delivery_date, Date),
                ).all()
            if user.last_delivery_date: 
                current_books = Order.query.filter_by(user_id=user.id).filter(
                    cast(Order.placed_on, Date) == cast(user.last_delivery_date, Date),
                ).all()
            bucket = user.get_next_bucket()
            if len(bucket) or len(delivery_books): 
                orders.append({
                    "user": user.to_json(),
                    "current_books": [order.to_json() for order in current_books],
                    "delivery_books": [order.to_json() for order in delivery_books],
                    "bucket": bucket
                })
        return orders

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username
        }
