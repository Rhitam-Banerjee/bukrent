from app import db
import uuid

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
    placed_on = db.Column(db.DateTime(timezone=True), server_default=func.now())

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