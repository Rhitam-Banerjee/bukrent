from app import db
import uuid

class CartBook(db.Model):
    __tablename__ = 'cart_books'
    id = db.Column(db.Integer, primary_key=True, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))

class WishlistBook(db.Model):
    __tablename__ = 'wishlist_books'
    id = db.Column(db.Integer, primary_key=True, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlist.id'))

class Cart(db.Model):
    __tablename__ = "cart"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    books = db.relationship('Book', secondary=CartBook.__table__)

    @staticmethod
    def create(user_id):
        cart_dict = dict(
            user_id = user_id
        )
        cart_obj = Cart(**cart_dict)
        db.session.add(cart_obj)
        db.session.commit()
        return cart_obj

    def add_book(self, book):
        self.books.append(book)
        db.session.add(self)
        db.session.commit()

class Wishlist(db.Model):
    __tablename__ = "wishlist"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    books = db.relationship('Book', secondary=WishlistBook.__table__)

    @staticmethod
    def create(user_id):
        wishlist_dict = dict(
            user_id = user_id
        )
        wishlist_obj = Wishlist(**wishlist_dict)
        db.session.add(wishlist_obj)
        db.session.commit()
        return wishlist_obj

    def add_book(self, book):
        self.books.append(book)
        db.session.add(self)
        db.session.commit()