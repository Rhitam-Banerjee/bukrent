from app import db
import uuid
from app.models.buckets import DeliveryBucket

from sqlalchemy.sql import func

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    book = db.relationship("Book")
    age_group = db.Column(db.Integer)

    billing_address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    shipping_address_id = db.Column(db.Integer, db.ForeignKey('address.id'))

    is_gift = db.Column(db.Boolean, default=False)
    gift_message = db.Column(db.String)
    placed_on = db.Column(db.Date)
    received_by = db.Column(db.String)
    is_completed = db.Column(db.Boolean, default=False)
    feedback = db.Column(db.String)
    delivery_time = db.Column(db.DateTime(timezone=True))
    delivery_address = db.Column(db.String)
    notes = db.Column(db.String)
    is_refused = db.Column(db.Boolean)
    is_taken = db.Column(db.Boolean, default=False)
    is_in_warehouse = db.Column(db.Boolean, default=False)

    @staticmethod
    def create(user_id, book_id, age_group, placed_on):
        order_dict = dict(
            guid = str(uuid.uuid4()),
            user_id = user_id,
            book_id = book_id,
            age_group = age_group,
            placed_on = placed_on
        )

        order_obj = Order(**order_dict)
        db.session.add(order_obj)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_json(self): 
        is_retained = False
        bucket_book = DeliveryBucket.query.filter_by(user_id=self.user_id, book_id=self.book_id, is_retained=True).first()
        if bucket_book and bucket_book.is_retained: 
            is_retained = True
        return {
            "id": self.id,
            "is_refused": self.is_refused,
            "is_in_warehouse": self.is_in_warehouse,
            "is_taken": self.is_taken,
            "is_retained": is_retained,
            "is_completed": self.is_completed,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "book": self.book.to_json(),
        }