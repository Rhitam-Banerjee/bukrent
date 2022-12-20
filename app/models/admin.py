from app import db
from app.models.user import User
from app.models.buckets import Suggestion, Wishlist, Dump
from app.models.order import Order
from app.models.category import Category
from app import db

class Admin(db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    def get_books(self, books): 
        final_books = []
        for book in books:
            tags = []
            book_json = book.to_json()
            for tag in book_json['categories']:
                tag_obj = Category.query.filter_by(name=tag).first()
                tags.append({"guid": tag_obj.guid, "name": tag_obj.name})
            suggestions = Suggestion.query.filter_by(book_id=book.id).all()
            wishlists = Wishlist.query.filter_by(book_id=book.id).all()
            dumps = Dump.query.filter_by(book_id=book.id, read_before=True).all()
            orders = Order.query.filter_by(book_id=book.id).all()
            suggested_users, wishlisted_users, previous_users = [], [], []
            for suggestion in suggestions: 
                try: 
                    user = User.query.get(suggestion.user_id).to_json()
                    if user not in suggested_users: 
                        suggested_users.append(user)
                except: 
                    pass
            for wishlist in wishlists: 
                try: 
                    user = User.query.get(wishlist.user_id).to_json()
                    if user not in wishlisted_users: 
                        wishlisted_users.append(user)
                except: 
                    pass
            for dump in dumps: 
                try: 
                    user = User.query.get(dump.user_id).to_json()
                    if user not in previous_users: 
                        previous_users.append(user)
                except: 
                    pass
            for order in orders: 
                try: 
                    user = User.query.get(order.user_id).to_json()
                    if user not in previous_users: 
                        previous_users.append(user)
                except: 
                    pass
            book_json['tags'] = tags
            book_json['suggested_users'] = self.get_users(suggested_users)
            book_json['wishlisted_users'] = self.get_users(wishlisted_users)
            book_json['previous_users'] = self.get_users(previous_users)
            final_books.append(book_json)
        return final_books

    def get_users(self, users): 
        all_users = []
        for user in users: 
            user_id = ''
            try: 
                user_id = user.id
            except: 
                user_id = user['id']
            user = User.query.get(user_id)
            all_users.append({
                "password": user.password,
                "wishlist": user.get_wishlist(),
                "suggestions": user.get_suggestions(),
                "previous": user.get_previous_books(),
                **user.to_json()
            })
        return all_users

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username
        }
