from app import db
import uuid

from app.models.buckets import *
from app.models.order import Order

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from sqlalchemy import and_

from datetime import date, timedelta, datetime

import random
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

    reading_level = db.Column(db.Integer)

    categories = db.relationship('Category', secondary=CategoryPreferences.__table__)
    formats = db.relationship('Format', secondary=FormatPreferences.__table__)
    authors = db.relationship('Author', secondary=AuthorPreferences.__table__)
    series = db.relationship('Series', secondary=SeriesPreferences.__table__)

    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)

    @staticmethod
    def create(last_book_read1, last_book_read2, last_book_read3, books_read_per_week, reading_level, categories, formats, authors, series, child_id):
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
            reading_level = reading_level,
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
        self.reading_level = preference_data.get('reading_level')

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

    def to_json(self):
        return {
            "guid": self.guid,
            "last_book_read1": self.last_book_read1,
            "last_book_read2": self.last_book_read2,
            "last_book_read3": self.last_book_read3,
            "books_read_per_week": self.books_read_per_week,
            "reading_level": self.reading_level,
            "categories": [category.guid for category in self.categories],
            "formats": [format.guid for format in self.formats],
            "authors": [author.guid for author in self.authors],
            "series": [serie.guid for serie in self.series],
        }

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

        kid_exists = False
        all_kids = Child.query.filter_by(user_id=user_id).all()
        for kid in all_kids:
            if child_json.get("name") == kid.name:
                kid_exists = True
        if not kid_exists:
            child_dict = dict(
                guid = str(uuid.uuid4()),
                name = child_json.get("name"),
                dob = datetime.strptime(child_json.get("dob"), '%Y-%m-%d'),
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

    def to_json(self):
        if self.preferences:
            return {
                "guid": self.guid,
                "name": self.name,
                "age_group": self.age_group,
                "dob": self.dob,
                "age": self.age,
                "preferences": self.preferences.to_json(),
            }
        else:
            return {
                "guid": self.guid,
                "name": self.name,
                "age_group": self.age_group,
                "dob": self.dob,
                "age": self.age,
            }

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
        if not all((address_json.get("area"), address_json.get("pin_code"))):
            raise ValueError("House Number, Building, Area and Pin Code are required!")

        existing_address = Address.query.filter_by(user_id=user_id).first()
        if not existing_address:
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
        else:
            return existing_address

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_json(self):
        return {
            "guid": self.guid,
            "house_number": self.house_number,
            "building": self.building,
            "area": self.area,
            "pincode": self.pincode,
            "landmark": self.landmark,
            "user_id": self.user_id,
        }

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    mobile_number = db.Column(db.String, unique=True)
    contact_number = db.Column(db.String, unique=True)
    source = db.Column(db.String)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    email = db.Column(db.String)
    password = db.Column(db.String)

    next_delivery_date = db.Column(db.Date)
    last_delivery_date = db.Column(db.Date)
    current_order = db.Column(db.Boolean, default=False)
    next_order_confirmed = db.Column(db.Boolean, default=False)

    has_child_1 = db.Column(db.Boolean, default=False)
    has_child_2 = db.Column(db.Boolean, default=False)
    has_child_3 = db.Column(db.Boolean, default=False)
    has_child_4 = db.Column(db.Boolean, default=False)
    has_child_5 = db.Column(db.Boolean, default=False)
    has_child_6 = db.Column(db.Boolean, default=False)

    newsletter = db.Column(db.Boolean, default=False)

    books_per_week = db.Column(db.Integer)
    payment_status = db.Column(db.String)
    plan_date = db.Column(db.Date, server_default=func.now())
    plan_duration = db.Column(db.Integer)
    is_subscribed = db.Column(db.Boolean, default=False)
    security_deposit = db.Column(db.Boolean, default=False)
    payment_id = db.Column(db.String)
    plan_id = db.Column(db.String)
    subscription_id = db.Column(db.String)
    order_id = db.Column(db.String)

    is_deleted = db.Column(db.Boolean, default=False)

    delivery_buckets = db.relationship(DeliveryBucket, lazy=True)
    book_dump = db.relationship(Dump, lazy=True)
    wishlist = db.relationship(Wishlist, lazy=True)
    suggestions = db.relationship(Suggestion, lazy=True)

    address = db.relationship(Address, lazy=True)
    order = db.relationship(Order, lazy=True)
    child = db.relationship(Child, lazy=True)

    #Orders

    def to_json(self):
        address = ""
        if len(self.address):
            address = self.address[0].to_json()
        return {
            "id": self.id,
            "guid": self.guid,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "next_delivery_date": self.next_delivery_date,
            "is_subscribed": self.is_subscribed,
            "plan_id": self.plan_id,
            "plan_date": self.plan_date,
            "plan_duration": self.plan_duration,
            "payment_status": self.payment_status,
            "subscription_id": self.subscription_id,
            "order_id": self.order_id,
            "payment_id": self.payment_id,
            "address": address,
            "children": [child.to_json() for child in self.child],
            "books_per_week": self.books_per_week,
            "mobile_number": self.mobile_number,
            "contact_number": self.contact_number,
            "source": self.source,
        }

    @staticmethod
    def create(first_name, last_name, mobile_number, password):
        user_dict = dict(
            guid = str(uuid.uuid4()),
            first_name = first_name,
            last_name = last_name,
            mobile_number = mobile_number,
            password = password
        )
        user_obj = User(**user_dict)
        db.session.add(user_obj)
        db.session.commit()

        return user_obj

    def delete(self):
        try:
            delivery_buckets = self.delivery_buckets
            for bucket in delivery_buckets:
                bucket.delete()
        except: pass
        try:
            book_dumps = self.book_dump
            for dump in book_dumps:
                dump.delete()
        except: pass
        try:
            wishlists = self.wishlist
            for wishlist in wishlists:
                wishlist.delete()
        except: pass
        try:
            suggestions = self.suggestions
            for suggestion in suggestions:
                suggestion.delete()
        except: pass
        try:
            addresses = self.address
            for address in addresses:
                address.delete()
        except: pass
        try:
            orders = self.order
            for order in orders:
                order.delete()
        except: pass
        db.session.delete(self)
        db.session.commit()

    def add_child(self, child_json):
        Child.create(child_json, self.id)

    def add_age_groups(self, age_groups):
        from app.models.books import Book

        suggestions = Suggestion.query.filter_by(user_id=self.id).all()
        books = []
        if len(suggestions) == 0:
            final_suggestions = []
            for age_group in age_groups:
                if age_group == 1:
                    self.has_child_1 = True
                    books = Book.query.filter_by(suggestion_age1=True).all()
                if age_group == 2:
                    self.has_child_2 = True
                    books = Book.query.filter_by(suggestion_age2=True).all()
                if age_group == 3:
                    self.has_child_3 = True
                    books = Book.query.filter_by(suggestion_age3=True).all()
                if age_group == 4:
                    self.has_child_4 = True
                    books = Book.query.filter_by(suggestion_age4=True).all()
                if age_group == 5:
                    self.has_child_5 = True
                    books = Book.query.filter_by(suggestion_age5=True).all()
                if age_group == 6:
                    self.has_child_6 = True
                    books = Book.query.filter_by(suggestion_age6=True).all()

                for book in books:
                    if book not in final_suggestions:
                        final_suggestions.append({
                            "book": book,
                            "age_group": age_group
                        })

            db.session.add(self)
            db.session.commit()

            for suggestion in final_suggestions:
                Suggestion.create(self.id, suggestion["book"].id, suggestion["age_group"])

    def update_details(self, email, password):
        self.email = email
        self.password = password
        db.session.add(self)
        db.session.commit()

    def update_plan(self, plan):
        if plan == 1:
            self.plan_id = os.environ.get("RZP_PLAN_1_ID")
            self.books_per_week = 1
        elif plan == 2:
            self.plan_id = os.environ.get("RZP_PLAN_2_ID")
            self.books_per_week = 2
        elif plan == 3:
            self.plan_id = os.environ.get("RZP_PLAN_3_ID")
            self.books_per_week = 4
        db.session.add(self)
        db.session.commit()

    def remove_plan(self):
        self.plan_id = ""
        db.session.add(self)
        db.session.commit()

    def add_to_wishlist(self, guid):
        from app.models.books import Book

        book = Book.query.filter_by(guid=guid).first()

        existing = Wishlist.query.filter(and_(Wishlist.user_id==self.id, Wishlist.book_id==book.id)).first()
        if not existing:
            Wishlist.create(self.id, book.id, 1)

    def suggestion_to_wishlist(self, guid):
        from app.models.books import Book

        book = Book.query.filter_by(guid=guid).first()
        suggestion = Suggestion.query.filter(and_(Suggestion.user_id==self.id, Suggestion.book_id==book.id)).first()
        age_group = suggestion.age_group
        suggestion.delete()

        wishlist_obj = Wishlist.create(self.id, book.id, age_group)

        # if not self.next_order_confirmed:
        #     books_per_week = self.books_per_week
        #     if wishlist_obj.priority_order <= books_per_week:
        #         if self.next_delivery_date:
        #             next_delivery_date = self.next_delivery_date
        #         else:
        #             next_delivery_date = date.today()
        #             self.next_delivery_date = date.today()
        #             db.session.add(self)
        #             db.session.commit()
        #         DeliveryBucket.create(self.id, book.id, next_delivery_date, age_group)

        # buckets = DeliveryBucket.query.filter(and_(DeliveryBucket.user_id==self.id, DeliveryBucket.delivery_date==self.next_delivery_date)).all()
        # if len(buckets) < self.books_per_week:
        #     DeliveryBucket.create(self.id, book.id, self.next_delivery_date, age_group)

    def suggestion_to_dump(self, guid):
        from app.models.books import Book

        book = Book.query.filter_by(guid=guid).first()
        suggestion = Suggestion.query.filter(and_(Suggestion.user_id==self.id, Suggestion.book_id==book.id)).first()
        suggestion.delete()

        Dump.create(self.id, book.id)

    def dump_action_read(self, guid):
        from app.models.books import Book

        book = Book.query.filter_by(guid=guid).first()
        dump = Dump.query.filter(and_(Dump.user_id==self.id, Dump.book_id==book.id)).first()

        dump.read_before = True
        dump.action_taken = True
        db.session.add(dump)
        db.session.commit()

    def dump_action_dislike(self, guid):
        from app.models.books import Book

        book = Book.query.filter_by(guid=guid).first()
        dump = Dump.query.filter(and_(Dump.user_id==self.id, Dump.book_id==book.id)).first()

        dump.disliked = True
        dump.action_taken = True
        db.session.add(dump)
        db.session.commit()

    def wishlist_next(self, guid):
        from app.models.books import Book

        book = Book.query.filter_by(guid=guid).first()

        first_item = Wishlist.query.filter(and_(Wishlist.user_id==self.id, Wishlist.book_id==book.id)).first()

        second_item = None

        next_priority_order = first_item.priority_order + 1
        while (second_item == None):
            second_item = Wishlist.query.filter(and_(Wishlist.user_id==self.id, Wishlist.priority_order==next_priority_order)).first()
            next_priority_order += 1

        ##Check if first item is in delivery bucket
        # if not self.next_order_confirmed:
        #     delivery_bucket_first = DeliveryBucket.query.filter(and_(DeliveryBucket.user_id==self.id, DeliveryBucket.book_id==book.id, DeliveryBucket.delivery_date==self.next_delivery_date)).first()
        #     delivery_bucket_second = DeliveryBucket.query.filter(and_(DeliveryBucket.user_id==self.id, DeliveryBucket.book_id==second_item.book.id, DeliveryBucket.delivery_date==self.next_delivery_date)).first()
        #     if delivery_bucket_first and delivery_bucket_second:
        #         pass
        #     elif delivery_bucket_first:
        #         delivery_bucket_first.delete()
        #         DeliveryBucket.create(self.id, second_item.book.id, self.next_delivery_date, second_item.age_group)

        first_priority_order = first_item.priority_order
        second_priority_order = second_item.priority_order

        first_item.priority_order = second_priority_order
        second_item.priority_order = first_priority_order

        db.session.add(first_item)
        db.session.add(second_item)
        db.session.commit()

    def wishlist_prev(self, guid):
        from app.models.books import Book

        book = Book.query.filter_by(guid=guid).first()

        second_item = Wishlist.query.filter(and_(Wishlist.user_id==self.id, Wishlist.book_id==book.id)).first()

        first_item = None

        prev_priority_order = second_item.priority_order - 1
        while (first_item == None):
            first_item = Wishlist.query.filter(and_(Wishlist.user_id==self.id, Wishlist.priority_order==prev_priority_order)).first()
            prev_priority_order -= 1

        ##Check if first item is in delivery bucket
        # if not self.next_order_confirmed:
        #     delivery_bucket_first = DeliveryBucket.query.filter(and_(DeliveryBucket.user_id==self.id, DeliveryBucket.book_id==first_item.book.id, DeliveryBucket.delivery_date==self.next_delivery_date)).first()
        #     delivery_bucket_second = DeliveryBucket.query.filter(and_(DeliveryBucket.user_id==self.id, DeliveryBucket.book_id==book.id, DeliveryBucket.delivery_date==self.next_delivery_date)).first()
        #     if delivery_bucket_first and delivery_bucket_second:
        #         pass
        #     elif delivery_bucket_first:
        #         delivery_bucket_first.delete()
        #         DeliveryBucket.create(self.id, second_item.book.id, self.next_delivery_date, second_item.age_group)

        second_priority_order = second_item.priority_order
        first_priority_order = first_item.priority_order

        second_item.priority_order = first_priority_order
        first_item.priority_order = second_priority_order

        db.session.add(second_item)
        db.session.add(first_item)
        db.session.commit()

    def wishlist_remove(self, guid):
        from app.models.books import Book

        book = Book.query.filter_by(guid=guid).first()
        wishlist = Wishlist.query.filter_by(user_id=self.id, book_id=book.id).first()

        # bucket_removed = False

        # if not self.next_order_confirmed:
        #     delivery_bucket = DeliveryBucket.query.filter(and_(DeliveryBucket.user_id==self.id, DeliveryBucket.book_id==book.id, DeliveryBucket.delivery_date==self.next_delivery_date)).first()
        #     if delivery_bucket:
        #         delivery_bucket.delete()
        #         bucket_removed = True

        wishlist.delete()
        Dump.create(self.id, book.id)

        # if bucket_removed:
        #     wishlists = Wishlist.query.filter_by(user_id=self.id).order_by(Wishlist.priority_order.asc()).all()
        #     for wishlist_obj in wishlists:
        #         existing_bucket = DeliveryBucket.query.filter(and_(DeliveryBucket.user_id==self.id, DeliveryBucket.book_id==wishlist_obj.book.id, DeliveryBucket.delivery_date==self.next_delivery_date)).first()
        #         if not existing_bucket:
        #             DeliveryBucket.create(self.id, wishlist_obj.book.id, self.next_delivery_date, wishlist_obj.age_group)
        #             break

        wishlists = Wishlist.query.filter_by(user_id=self.id).order_by(Wishlist.priority_order.asc()).all()
        current_priority_order = 1
        for wishlist in wishlists:
            wishlist.priority_order = current_priority_order
            db.session.add(wishlist)
            db.session.commit()

            current_priority_order += 1

    def create_bucket_list(self):
        try:
            print(self.books_per_week)
            total_books = self.books_per_week

            wishlists = Wishlist.query.filter_by(user_id=self.id).order_by(Wishlist.priority_order.asc()).all()

            if len(wishlists) < total_books:
                raise ValueError("Not enough books in wishlist!")

            for wishlist in wishlists[:total_books]:
                DeliveryBucket.create(self.id, wishlist.book_id, self.next_delivery_date, wishlist.age_group)
                wishlist.delete()

            wishlists = Wishlist.query.filter_by(user_id=self.id).order_by(Wishlist.priority_order.asc()).all()

            for i, wishlist in enumerate(wishlists):
                wishlist.priority_order = i+1
                db.session.add(wishlist)

            db.session.commit()

        except Exception as e:
            raise ValueError(str(e))

    def confirm_order(self):
        try:
            if not self.next_delivery_date:
                raise ValueError(f"Please set a delivery date first")
            if self.last_delivery_date and date.today() <= self.last_delivery_date:
                raise ValueError(f"Wait until {self.last_delivery_date + timedelta(days=1)} to place a new order")

            buckets = self.delivery_buckets

            for bucket in buckets:
                if bucket.book.stock_available <= 0:
                    raise ValueError(f"Book - {bucket.book.name} with ISBN {bucket.book.isbn} is out of stock!")

            for bucket in buckets:
                Order.create(self.id, bucket.book.id, bucket.age_group, self.next_delivery_date)
                bucket.delete()

            next_delivery_date = self.next_delivery_date
            self.last_delivery_date = next_delivery_date
            self.next_delivery_date = next_delivery_date + timedelta(days=7)
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            raise ValueError(str(e))

    def bucket_remove(self, guid):
        from app.models.books import Book

        book = Book.query.filter_by(guid=guid).first()
        bucket = DeliveryBucket.query.filter(and_(DeliveryBucket.user_id==self.id, DeliveryBucket.book_id==book.id)).first()


        wishlists = Wishlist.query.filter_by(user_id=self.id).order_by(Wishlist.priority_order.asc()).all()
        if not len(wishlists):
            raise ValueError("No book to replace! Add some books in your wishlist.")

        wishlist = wishlists[0]

        Wishlist.create(self.id, bucket.book_id, bucket.age_group)
        bucket.delete()
        DeliveryBucket.create(self.id, wishlist.book_id, self.next_delivery_date, wishlist.age_group)

        wishlist.delete()

        db.session.commit()

    def remove_from_previous(self, guid): 
        from app.models.books import Book
        from app.models.buckets import Dump

        book = Book.query.filter_by(guid=guid).first()

        order = Order.query.filter_by(user_id=self.id, book_id=book.id).first()

        if order and (not self.next_delivery_date or self.next_delivery_date.strftime('%Y-%m-%d') != order.placed_on.strftime('%Y-%m-%d')): 
            order.delete()
        else: 
            dump = Dump.query.filter_by(user_id=self.id, book_id=book.id).first()
            if dump: 
                dump.delete()

        db.session.commit()

    def change_delivery_date(self, delivery_date):
        delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d')

        if delivery_date <= datetime.today() or (self.last_delivery_date and delivery_date.date() <= self.last_delivery_date):
            raise ValueError("Invalid delivery date")

        buckets = DeliveryBucket.query.filter(and_(DeliveryBucket.user_id==self.id, DeliveryBucket.delivery_date==self.next_delivery_date)).all()

        for bucket in buckets:
            bucket.delivery_date = delivery_date
            db.session.add(bucket)
            db.session.commit()

        self.next_delivery_date = delivery_date
        db.session.add(self)
        db.session.commit()

    def retain_book(self, guid):
        from app.models.books import Book

        book = Book.query.filter_by(guid=guid).first()
        buckets = self.delivery_buckets

        if len(buckets) == 0:
            raise ValueError("No books yet in the bucket. They're updated 2 days before your delivery date!")

        for bucket in buckets[::-1]:
            if not bucket.is_retained:
                Wishlist.create(self.id, bucket.book_id, bucket.age_group)
                bucket.remove()
                break

        order = Order.query.filter(and_(Order.user_id==self.id, order.book_id==book.id)).first()
        DeliveryBucket.create(self.id, book.id, self.next_delivery_date, order.age_group, is_retained=True)

    def retain_current_book(self, guid):
        from app.models.books import Book
        book = Book.query.filter_by(guid=guid).first()
        existing = Wishlist.query.filter(and_(Wishlist.user_id==self.id, Wishlist.book_id==book.id)).first()
        if not existing:
            Wishlist.create(self.id, book.id, 1)
            order = Order.query.filter_by(user_id=self.id, book_id=guid).first()
            if order:
                order.placed_on = None
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
        self.payment_status = 'Paid'
        self.plan_date = date.today()
        db.session.add(self)
        db.session.commit()

    def update_subscription_details(self, subscription_id, payment_id):
        self.subscription_id = subscription_id
        self.payment_id = payment_id
        self.security_deposit = True
        self.is_subscribed = True
        self.payment_status = 'Paid'
        self.plan_date = date.today()
        db.session.add(self)
        db.session.commit()

    def get_suggestions(self):
        suggestions = self.suggestions

        book_list = []
        for suggestion in suggestions:
            if suggestion.book.stock_available > 0:
                temp_dict = {
                    "name": suggestion.book.name,
                    "guid": suggestion.book.guid,
                    "isbn": suggestion.book.isbn,
                    "image": suggestion.book.image
                    # "age_group": suggestion.age_group
                }

                book_list.append(temp_dict)

        return book_list

    def get_dump_data(self):
        dumps = self.book_dump

        book_list = []
        for dump in dumps:
            if not dump.action_taken:
                temp_dict = {
                    "name": dump.book.name,
                    "guid": dump.book.guid,
                    "isbn": dump.book.isbn,
                    "image": dump.book.image
                }

                book_list.append(temp_dict)

        return book_list

    def get_read_books(self):
        read_books = Dump.query.filter_by(user_id=self.id, read_before=True).all()
        book_list = []
        for read_book in read_books:
            temp_dict = {
                "name": read_book.book.name,
                "guid": read_book.book.guid,
                "isbn": read_book.book.isbn,
                "image": read_book.book.image
            }

            book_list.append(temp_dict)

        return book_list

    def get_previous_books(self):
        orders = Order.query.filter_by(user_id=self.id).all()
        read_books = self.get_read_books()
        books = []
        for order in orders: 
            if order.book: 
                books.append(order.book.to_json())
        for book in read_books:
            if book: 
                books.append(book)
        return books

    def get_current_books(self):
        orders = Order.query.filter_by(user_id=self.id).all()
        books = []
        last_delivery_date = self.last_delivery_date.strftime('%Y-%m-%d')
        for order in orders:
            if last_delivery_date == order.placed_on.strftime('%Y-%m-%d'):
                if order.book: 
                    books.append(order.book.to_json())
        return books

    def get_wishlist(self):
        wishlists = Wishlist.query.filter_by(user_id=self.id).order_by(Wishlist.priority_order.asc()).all()
        book_list = []
        for i, wishlist in enumerate(wishlists):
            temp_dict = {
                "name": wishlist.book.name,
                "guid": wishlist.book.guid,
                "isbn": wishlist.book.isbn,
                # "age_group": wishlist.age_group,
                "available": True if wishlist.book.stock_available > 0 else False,
                "image": wishlist.book.image
            }

            if i == 0:
                temp_dict["position"] = "first"
            elif i+1 == len(wishlists):
                temp_dict["position"] = "last"
            else:
                temp_dict["position"] = "middle"

            book_list.append(temp_dict)

        return book_list

    def get_next_bucket(self):
        buckets = self.delivery_buckets

        book_list = []
        for bucket in buckets:
            temp_dict = {
                "name": bucket.book.name,
                "guid": bucket.book.guid,
                "isbn": bucket.book.isbn,
                "image": bucket.book.image
                # "age_group": bucket.age_group
            }

            book_list.append(temp_dict)

        return book_list

    def get_previous_bucket(self):
        from app.models.order import Order

        orders = Order.query.filter_by(user_id=self.id).order_by(Order.placed_on.desc()).all()

        if len(orders) > 0:
            last_date = orders[0].placed_on

            last_orders = Order.query.filter(and_(Order.user_id==self.id, Order.placed_on==last_date)).all()

            book_list = []
            for order in last_orders:
                temp_dict = {
                    "name": order.book.name,
                    "guid": order.book.guid,
                    "isbn": order.book.isbn,
                    "image": order.book.image
                    # "age_group": order.age_group
                }

                book_list.append(temp_dict)

            return book_list
        else:
            return []
