from app import db
import uuid

class Dump(db.Model):
    __tablename__ = "dump"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    book = db.relationship("Book")
    read_before = db.Column(db.Boolean, default=False)
    disliked = db.Column(db.Boolean, default=False)
    action_taken = db.Column(db.Boolean, default=False)

    @staticmethod
    def create(user_id, book_id):
        dump_dict = dict(
            user_id = user_id,
            book_id = book_id
        )
        dump_obj = Dump(**dump_dict)
        db.session.add(dump_obj)
        db.session.commit()
        return dump_obj

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class DeliveryBucket(db.Model):
    __tablename__ = "delivery_bucket"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    book = db.relationship("Book")
    priority_order = db.Column(db.Integer)
    delivery_date = db.Column(db.Date)
    age_group = db.Column(db.Integer)
    is_retained = db.Column(db.Boolean, default=False)

    @staticmethod
    def create(user_id, book_id, delivery_date, age_group, is_retained=False):
        bucket_dict = dict(
            user_id = user_id,
            book_id = book_id,
            delivery_date = delivery_date,
            age_group = age_group,
            is_retained = is_retained
        )

        buckets = DeliveryBucket.query.filter_by(delivery_date=delivery_date).order_by(DeliveryBucket.priority_order.desc()).first()
        if buckets:
            bucket_dict["priority_order"] = buckets.priority_order + 1
        else:
            bucket_dict["priority_order"] = 1
            
        bucket_obj = DeliveryBucket(**bucket_dict)
        db.session.add(bucket_obj)
        db.session.commit()
        return bucket_obj

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_json(self): 
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "book": self.book.to_json(),
            "delivery_date": self.delivery_date,
            "is_retained": self.is_retained
        }

class Wishlist(db.Model):
    __tablename__ = "wishlist"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    book = db.relationship("Book")
    priority_order = db.Column(db.Integer)
    age_group = db.Column(db.Integer)

    @staticmethod
    def create(user_id, book_id, age_group):
        wishlist_dict = dict(
            user_id = user_id,
            book_id = book_id,
            age_group = age_group
        )

        wishlists = Wishlist.query.filter_by(user_id=user_id).order_by(Wishlist.priority_order.desc()).first()
        if wishlists:
            wishlist_dict["priority_order"] = wishlists.priority_order + 1
        else:
            wishlist_dict["priority_order"] = 1

        wishlist_obj = Wishlist(**wishlist_dict)
        db.session.add(wishlist_obj)
        db.session.commit()
        return wishlist_obj

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Suggestion(db.Model):
    __tablename__ = "suggestion"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    book = db.relationship("Book")
    age_group = db.Column(db.Integer)

    @staticmethod
    def create(user_id, book_id, age_group):
        suggestion_dict = dict(
            user_id = user_id,
            book_id = book_id,
            age_group = age_group
        )

        suggestion_obj = Suggestion(**suggestion_dict)
        db.session.add(suggestion_obj)
        db.session.commit()
        return suggestion_obj

    def delete(self):
        db.session.delete(self)
        db.session.commit()