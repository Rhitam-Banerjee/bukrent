from app import db
import uuid

from app.models.annotations import Annotation
from app.models.reviews import Review
from app.models.details import Detail

class BookCategory(db.Model):
    __tablename__ = 'book_categories'
    id = db.Column(db.Integer, primary_key=True, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

class BookAuthor(db.Model):
    __tablename__ = 'book_authors'
    id = db.Column(db.Integer, primary_key=True, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))

class BookPublisher(db.Model):
    __tablename__ = 'book_publishers'
    id = db.Column(db.Integer, primary_key=True, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'))

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    isbn = db.Column(db.String, nullable=False)
    rating = db.Column(db.String)
    review_count = db.Column(db.String, nullable=False)
    book_format = db.Column(db.String, nullable=False)
    language = db.Column(db.String, nullable=False)
    price = db.Column(db.String)
    description = db.Column(db.String, nullable=False)
    borrowed = db.Column(db.Integer, default=0)
    
    details = db.relationship(Detail, lazy=True, uselist=False)
    annotation = db.relationship(Annotation, lazy=True, uselist=False)
    reviews = db.relationship(Review, lazy=True)

    series_id = db.Column(db.Integer, db.ForeignKey('series.id'))

    categories = db.relationship('Category', secondary=BookCategory.__table__)
    authors = db.relationship('Author', secondary=BookAuthor.__table__)
    publishers = db.relationship('Publisher', secondary=BookPublisher.__table__)

    @staticmethod
    def create(name, image, isbn, rating, review_count, book_format, language, price, description, series_id):
        book_dict = dict(
            guid = str(uuid.uuid4()),
            name = name,
            image = image,
            isbn = isbn,
            rating = rating,
            review_count = review_count,
            book_format = book_format,
            language = language,
            price = price,
            description = description
        )

        if series_id:
            book_dict["series_id"] = series_id

        book_obj = Book(**book_dict)
        db.session.add(book_obj)
        db.session.commit()

    @staticmethod
    def get_more_books(detail):
        objs = Detail.query.filter_by(age_group=detail.age_group).order_by(Detail.bestseller_rank.asc()).limit(10).all()
        return [Book.query.filter_by(id=obj.book_id).first() for obj in objs]

    # def to_json(self):
    #     return {
    #         "name": self.name,
    #         "image": self.image,
    #         "rating": self.rating,
    #         "review_count": self.review_count,
    #         "book_format": self.book_format,
    #         "language": self.language,
    #         "price": self.price,
    #         "description": self.description,
    #         "details": self.details.to_json(),
    #         "annotations": self.annotation.to_json() if self.annotation else {},
    #         "reviews": self.reviews.to_json() if self.reviews else {},
    #         "categories": [category.name for category in self.categories],
    #         "authors": [author.name for author in self.authors]
    #     }