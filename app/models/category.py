from app import db
import uuid

from app.models.books import BookCategory
from app.models.user import CategoryPreferences

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    age1 = db.Column(db.Boolean, default=False)
    age2 = db.Column(db.Boolean, default=False)
    age3 = db.Column(db.Boolean, default=False)
    age4 = db.Column(db.Boolean, default=False)
    age5 = db.Column(db.Boolean, default=False)
    age6 = db.Column(db.Boolean, default=False)
    total_books = db.Column(db.Integer)
    display = db.Column(db.Boolean, default=False)
    books = db.relationship('Book', secondary=BookCategory.__table__)
    preferences = db.relationship('Preference', secondary=CategoryPreferences.__table__)

    @staticmethod
    def create(name, age1, age2, age3, age4, age5, age6, total_books, display):
        category_dict = dict(
            guid = str(uuid.uuid4()),
            name = name,
            age1 = age1,
            age2 = age2,
            age3 = age3,
            age4 = age4,
            age5 = age5,
            age6 = age6,
            total_books = total_books,
            display = display
        )
        category_obj = Category(**category_dict)
        db.session.add(category_obj)
        db.session.commit()