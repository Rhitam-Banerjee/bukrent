from app import db
import uuid

from app.models.cart import Cart, Wishlist
from app.models.order import Order

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func

from datetime import date

import os

class CategoryPreferences(db.Model):
    __tablename__ = 'category_preferences'
    id = db.Column(db.Integer, primary_key=True, index=True)
    preference_id = db.Column(db.Integer, db.ForeignKey('preferences.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

class FormatPreferences(db.Model):
    __tablename__ = 'format_preferences'
    id = db.Column(db.Integer, primary_key=True, index=True)
    preference_id = db.Column(db.Integer, db.ForeignKey('preferences.id'))
    format_id = db.Column(db.Integer, db.ForeignKey('formats.id'))

class AuthorPreferences(db.Model):
    __tablename__ = 'author_preferences'
    id = db.Column(db.Integer, primary_key=True, index=True)
    preference_id = db.Column(db.Integer, db.ForeignKey('preferences.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))

class SeriesPreferences(db.Model):
    __tablename__ = 'series_preferences'
    id = db.Column(db.Integer, primary_key=True, index=True)
    preference_id = db.Column(db.Integer, db.ForeignKey('preferences.id'))
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'))

class Preference(db.Model):
    __tablename__ = "preferences"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    last_book_read1 = db.Column(db.String)
    last_book_read2 = db.Column(db.String)
    last_book_read3 = db.Column(db.String)

    books_read_per_week = db.Column(db.Integer)

    categories = db.relationship('Category', secondary=CategoryPreferences.__table__)
    formats = db.relationship('Format', secondary=FormatPreferences.__table__)
    authors = db.relationship('Author', secondary=AuthorPreferences.__table__)
    series = db.relationship('Series', secondary=SeriesPreferences.__table__)

    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)

    @staticmethod
    def create(last_book_read1, last_book_read2, last_book_read3, books_read_per_week, categories, formats, authors, series, child_id):
        from app.models.format import Format
        from app.models.author import Author
        from app.models.series import Series
        from app.models.category import Category

        preference_dict = dict(
            guid = str(uuid.uuid4()),
            last_book_read1 = last_book_read1,
            last_book_read2 = last_book_read2,
            last_book_read3 = last_book_read3,
            books_read_per_week = books_read_per_week,
            child_id = child_id
        )

        category_list = []
        for category_guid in categories:
            category_list.append(Category.query.filter_by(guid=category_guid).first())

        format_list = []
        for format_guid in formats:
            format_list.append(Format.query.filter_by(guid=format_guid).first())

        author_list = []
        for author_guid in authors:
            author_list.append(Author.query.filter_by(guid=author_guid).first())

        series_list = []
        for series_guid in series:
            series_list.append(Series.query.filter_by(guid=series_guid).first())

        preference_dict["categories"] = category_list
        preference_dict["formats"] = format_list
        preference_dict["authors"] = author_list
        preference_dict["series"] = series_list

        preference_obj = Preference(**preference_dict)
        db.session.add(preference_obj)
        db.session.commit()

    def update(self, preference_data):
        from app.models.format import Format
        from app.models.author import Author
        from app.models.series import Series
        from app.models.category import Category

        self.last_book_read1 = preference_data.get("last_book_read1")
        self.last_book_read2 = preference_data.get("last_book_read2")
        self.last_book_read3 = preference_data.get("last_book_read3")
        self.books_read_per_week = preference_data.get("books_read_per_week")

        self.categories = []
        self.formats = []
        self.authors = []
        self.series = []
        
        db.session.add(self)
        db.session.commit()

        category_list = []
        for category_guid in preference_data.get("categories"):
            category_list.append(Category.query.filter_by(guid=category_guid).first())

        format_list = []
        for format_guid in preference_data.get("formats"):
            format_list.append(Format.query.filter_by(guid=format_guid).first())

        author_list = []
        for author_guid in preference_data.get("authors"):
            author_list.append(Author.query.filter_by(guid=author_guid).first())

        series_list = []
        for series_guid in preference_data.get("series"):
            series_list.append(Series.query.filter_by(guid=series_guid).first())

        self.categories = category_list
        self.formats = format_list
        self.authors = author_list
        self.series = series_list

        db.session.add(self)
        db.session.commit()

class Child(db.Model):
    __tablename__ = "children"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String)
    dob = db.Column(db.Date)
    age_group = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    preferences = db.relationship(Preference, lazy=True, uselist=False)

    @hybrid_property
    def age(self):
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

    @staticmethod
    def create(child_json, user_id):
        if not all((child_json.get("name"), child_json.get("dob"), child_json.get("age_group"))):
            raise ValueError("All fields for all the kids are necessary.")

        child_dict = dict(
            guid = str(uuid.uuid4()),
            name = child_json.get("name"),
            dob = child_json.get("dob"),
            age_group = child_json.get("age_group"),
            user_id = user_id
        )
        child_obj = Child(**child_dict)
        db.session.add(child_obj)
        db.session.commit()

    def delete(self):
        if self.preferences:
            db.session.delete(self.preferences)
        db.session.delete(self)
        db.session.commit()

class Address(db.Model):
    __tablename__ = "address"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    house_number = db.Column(db.String)
    building = db.Column(db.String)
    area = db.Column(db.String)
    pincode = db.Column(db.String)
    landmark = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def create(address_json, user_id):
        if not all((address_json.get("house_number"), address_json.get("building"), address_json.get("area"), address_json.get("pin_code"))):
            raise ValueError("House Number, Building, Area and Pin Code are required!")

        address_dict = dict(
            guid = str(uuid.uuid4()),
            house_number = address_json.get("house_number"),
            building = address_json.get("building"),
            area = address_json.get("area"),
            pincode = address_json.get("pin_code"),
            landmark = address_json.get("landmark") or "",
            user_id = user_id
        )
        address_obj = Address(**address_dict)
        db.session.add(address_obj)
        db.session.commit()

        return address_obj

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    mobile_number = db.Column(db.String, unique=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    email = db.Column(db.String)
    password = db.Column(db.String)

    newsletter = db.Column(db.Boolean, default=False)

    is_subscribed = db.Column(db.Boolean, default=False)
    security_deposit = db.Column(db.Boolean, default=False)
    payment_id = db.Column(db.String)
    plan_id = db.Column(db.String)
    subscription_id = db.Column(db.String)
    order_id = db.Column(db.String)

    cart = db.relationship(Cart, lazy=True, uselist=False)
    wishlist = db.relationship(Wishlist, lazy=True, uselist=False)

    address = db.relationship(Address, lazy=True)
    order = db.relationship(Order, lazy=True)
    child = db.relationship(Child, lazy=True)
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
    def create(first_name, last_name, mobile_number):
        user_dict = dict(
            guid = str(uuid.uuid4()),
            first_name = first_name,
            last_name = last_name,
            mobile_number = mobile_number
        )
        user_obj = User(**user_dict)
        db.session.add(user_obj)
        db.session.commit()

        user_obj.add_cart_and_wishlist()

        return user_obj

    def delete(self):
        try:
            db.session.delete(self.cart)
        except: pass
        try:
            db.session.delete(self.wishlist)
        except: pass
        try:
            db.session.delete(self.address)
        except: pass
        db.session.delete(self)
        db.session.commit()

    def add_child(self, child_json):
        Child.create(child_json, self.id)

    def update_details(self, email, password):
        self.email = email
        self.password = password
        db.session.add(self)
        db.session.commit()

    def update_plan(self, plan):
        if plan == 1:
            self.plan_id = os.environ.get("RZP_PLAN_1_ID")
        elif plan == 2:
            self.plan_id = os.environ.get("RZP_PLAN_2_ID")
        elif plan == 3:
            self.plan_id = os.environ.get("RZP_PLAN_3_ID")
        db.session.add(self)
        db.session.commit()

    def remove_plan(self):
        self.plan_id = ""
        db.session.add(self)
        db.session.commit()

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

    def add_subscription_details(self, subscription_id):
        self.subscription_id = subscription_id
        db.session.add(self)
        db.session.commit()

    def add_order_details(self, order_id):
        self.order_id = order_id
        db.session.add(self)
        db.session.commit()

    def update_payment_details(self, order_id, payment_id):
        self.order_id = order_id
        self.payment_id = payment_id
        self.security_deposit = True
        self.is_subscribed = True
        db.session.add(self)
        db.session.commit()

    def update_subscription_details(self, subscription_id, payment_id):
        self.subscription_id = subscription_id
        self.payment_id = payment_id
        self.security_deposit = True
        self.is_subscribed = True
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