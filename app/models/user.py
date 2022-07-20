from app import db
import uuid

from app.models.cart import Cart, Wishlist
from app.models.order import Order

from sqlalchemy.ext.hybrid import hybrid_property

import os

class Address(db.Model):
    __tablename__ = "address"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    house_number = db.Column(db.String)
    area = db.Column(db.String)
    city = db.Column(db.String)
    pincode = db.Column(db.String)
    country = db.Column(db.String)
    landmark = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def create(address_json, user_id):
        if not all((address_json.get("house_number"), address_json.get("area"), address_json.get("city"), address_json.get("pincode"), address_json.get("country"))):
            raise ValueError("House Number, Area, City, Country and Pin Code are required!")

        address_dict = dict(
            guid = str(uuid.uuid4()),
            house_number = address_json.get("house_number"),
            area = address_json.get("area"),
            city = address_json.get("city"),
            pincode = address_json.get("pincode"),
            country = address_json.get("country"),
            landmark = address_json.get("landmark") or "",
            user_id = user_id
        )
        address_obj = Address(**address_dict)
        db.session.add(address_obj)
        db.session.commit()

        return address_obj

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String)
    age = db.Column(db.String)
    child_name = db.Column(db.String)
    mobile_number = db.Column(db.String, unique=True)
    newsletter = db.Column(db.Boolean, default=False)
    is_subscribed = db.Column(db.Boolean, default=False)
    security_deposit = db.Column(db.Boolean, default=False)
    customer_id = db.Column(db.String)
    plan_id = db.Column(db.String)
    subscription_id = db.Column(db.String)

    cart = db.relationship(Cart, lazy=True, uselist=False)
    wishlist = db.relationship(Wishlist, lazy=True, uselist=False)

    address = db.relationship(Address, lazy=True)
    order = db.relationship(Order, lazy=True)
    #Orders

    @hybrid_property
    def books_per_week(self):
        if self.plan_id == os.environ.get("RZP_PLAN_1_ID"):
            return 1
        elif self.plan_id == os.environ.get("RZP_PLAN_2_ID"):
            return 2
        elif self.plan_id == os.environ.get("RZP_PLAN_3_ID"):
            return 4
        else:
            return 0

    @staticmethod
    def create(name, age, child_name, mobile_number):
        user_dict = dict(
            guid = str(uuid.uuid4()),
            name = name,
            age = age,
            child_name = child_name,
            mobile_number = mobile_number
        )
        user_obj = User(**user_dict)
        db.session.add(user_obj)
        db.session.commit()

        user_obj.add_cart_and_wishlist()

        return user_obj

    def add_cart_and_wishlist(self):
        cart = Cart.create(self.id)
        wishlist = Wishlist.create(self.id)
        self.cart = cart
        self.wishlist = wishlist
        db.session.add(self)
        db.session.commit()

    def move_book_to_wishlist(self, book):
        cart = self.cart
        wishlist = self.wishlist

        cart.books.remove(book)
        db.session.add(cart)

        wishlist.add_book(book)
        db.session.add(wishlist)

        db.session.commit()

    def move_book_to_cart(self, book):
        wishlist = self.wishlist
        cart = self.cart

        wishlist.books.remove(book)
        db.session.add(wishlist)

        cart.add_book(book)
        db.session.add(cart)

        db.session.commit()

    def remove_book_from_cart(self, book):
        cart = self.cart
        cart.books.remove(book)
        db.session.add(cart)
        db.session.commit()

    def remove_book_from_wishlist(self, book):
        wishlist = self.wishlist
        wishlist.books.remove(book)
        db.session.add(wishlist)
        db.session.commit()

    def add_subscription_details(self, plan, plan_id, subscription_id):
        self.plan_id = plan_id
        self.subscription_id = subscription_id
        db.session.add(self)
        db.session.commit()

    def add_customer_id(self, customer_id):
        self.customer_id = customer_id
        self.is_subscribed = True
        self.security_deposit = True
        db.session.add(self)
        db.session.commit()

    def add_books_to_cart_and_wishlist(self, cart, wishlist):
        from app.models.books import Book

        for item in cart:
            Cart.create(self.id)
            book = Book.query.filter_by(guid=item).first()
            self.cart.add_book(book)

        for item in wishlist:
            Wishlist.create(self.id)
            book = Book.query.filter_by(guid=item).first()
            self.wishlist.add_book(book)