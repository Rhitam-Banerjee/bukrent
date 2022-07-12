from app import db
import uuid

from sqlalchemy.sql import func

class OrderBook(db.Model):
    __tablename__ = 'order_books'
    id = db.Column(db.Integer, primary_key=True, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    billing_address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    shipping_address_id = db.Column(db.Integer, db.ForeignKey('address.id'))

    is_gift = db.Column(db.Boolean, default=False)
    gift_message = db.Column(db.String)

    books = db.relationship('Book', secondary=OrderBook.__table__)

    placed_on = db.Column(db.DateTime(timezone=True), server_default=func.now())

    @staticmethod
    def create(user_id, billing_address_id, shipping_address_id, is_gift, gift_message, books):
        from app.models.books import Book

        order_dict = dict(
            guid = str(uuid.uuid4()),
            user_id = user_id,
            billing_address_id = billing_address_id,
            shipping_address_id = shipping_address_id,
            is_gift = is_gift,
            gift_message = gift_message
        )

        book_objs = []
        for book in books:
            book_objs.append(Book.query.filter_by(guid=book).first())

        order_dict["books"] = book_objs

        order_obj = Order(**order_dict)
        db.session.add(order_obj)
        db.session.commit()