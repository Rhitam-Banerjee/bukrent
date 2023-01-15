from app import db
import uuid

from app.models.annotations import Annotation
from app.models.reviews import Review
from app.models.details import Detail
from app.models.buckets import DeliveryBucket, Wishlist, Suggestion, Dump
from app.models.order import Order

class BookCategory(db.Model):
    __tablename__ = 'book_categories'
    id = db.Column(db.Integer, primary_key=True, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

class BookFormat(db.Model):
    __tablename__ = 'book_formats'
    id = db.Column(db.Integer, primary_key=True, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    format_id = db.Column(db.Integer, db.ForeignKey('formats.id'))

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
    stock_available = db.Column(db.Integer)
    rentals = db.Column(db.Integer, default=0)

    amazon_bestseller = db.Column(db.Boolean, default=False)
    bestseller_age1 = db.Column(db.Boolean, default=False)
    bestseller_age2 = db.Column(db.Boolean, default=False)
    bestseller_age3 = db.Column(db.Boolean, default=False)
    bestseller_age4 = db.Column(db.Boolean, default=False)
    bestseller_age5 = db.Column(db.Boolean, default=False)
    bestseller_age6 = db.Column(db.Boolean, default=False)

    most_borrowed = db.Column(db.Boolean, default=False)
    borrowed_age1 = db.Column(db.Boolean, default=False)
    borrowed_age2 = db.Column(db.Boolean, default=False)
    borrowed_age3 = db.Column(db.Boolean, default=False)
    borrowed_age4 = db.Column(db.Boolean, default=False)
    borrowed_age5 = db.Column(db.Boolean, default=False)
    borrowed_age6 = db.Column(db.Boolean, default=False)

    suggestion_age1 = db.Column(db.Boolean, default=False)
    suggestion_age2 = db.Column(db.Boolean, default=False)
    suggestion_age3 = db.Column(db.Boolean, default=False)
    suggestion_age4 = db.Column(db.Boolean, default=False)
    suggestion_age5 = db.Column(db.Boolean, default=False)
    suggestion_age6 = db.Column(db.Boolean, default=False)

    age_group_1 = db.Column(db.Boolean, default=False)
    age_group_2 = db.Column(db.Boolean, default=False)
    age_group_3 = db.Column(db.Boolean, default=False)
    age_group_4 = db.Column(db.Boolean, default=False)
    age_group_5 = db.Column(db.Boolean, default=False)
    age_group_6 = db.Column(db.Boolean, default=False)

    tag1 = db.Column(db.String, default=False)

    details = db.relationship(Detail, lazy=True, uselist=False)
    annotation = db.relationship(Annotation, lazy=True, uselist=False)
    reviews = db.relationship(Review, lazy=True)

    series_id = db.Column(db.Integer, db.ForeignKey('series.id'))

    categories = db.relationship('Category', secondary=BookCategory.__table__)
    authors = db.relationship('Author', secondary=BookAuthor.__table__)
    publishers = db.relationship('Publisher', secondary=BookPublisher.__table__)

    @staticmethod
    def create(name, image, isbn, rating, review_count, book_format, language, price, description, stock_available, series_id, bestseller_json, borrowed_json, suggestion_json):
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
            description = description,
            stock_available = stock_available,
            rentals = 0
        )

        if bestseller_json:
            book_dict["amazon_bestseller"] = True
            book_dict["bestseller_age1"] = bestseller_json.get("bestseller_age1")
            book_dict["bestseller_age2"] = bestseller_json.get("bestseller_age2")
            book_dict["bestseller_age3"] = bestseller_json.get("bestseller_age3")
            book_dict["bestseller_age4"] = bestseller_json.get("bestseller_age4")
            book_dict["bestseller_age5"] = bestseller_json.get("bestseller_age5")
            book_dict["bestseller_age6"] = bestseller_json.get("bestseller_age6")

        if borrowed_json:
            book_dict["most_borrowed"] = True
            book_dict["borrowed_age1"] = borrowed_json.get("borrowed_age1")
            book_dict["borrowed_age2"] = borrowed_json.get("borrowed_age2")
            book_dict["borrowed_age3"] = borrowed_json.get("borrowed_age3")
            book_dict["borrowed_age4"] = borrowed_json.get("borrowed_age4")
            book_dict["borrowed_age5"] = borrowed_json.get("borrowed_age5")
            book_dict["borrowed_age6"] = borrowed_json.get("borrowed_age6")

        if suggestion_json:
            book_dict["suggestion_age1"] = suggestion_json.get("suggestion_age1")
            book_dict["suggestion_age2"] = suggestion_json.get("suggestion_age2")
            book_dict["suggestion_age3"] = suggestion_json.get("suggestion_age3")
            book_dict["suggestion_age4"] = suggestion_json.get("suggestion_age4")
            book_dict["suggestion_age5"] = suggestion_json.get("suggestion_age5")
            book_dict["suggestion_age6"] = suggestion_json.get("suggestion_age6")

        if series_id:
            book_dict["series_id"] = series_id

        book_obj = Book(**book_dict)
        db.session.add(book_obj)
        db.session.commit()

    def delete(self):
        try:
            authors = BookAuthor.query.filter_by(book_id=self.id).all()
            for author in authors:
                db.session.delete(author)
        except: pass
        try:
            categories = BookCategory.query.filter_by(book_id=self.id).all()
            for category in categories:
                db.session.delete(category)
        except: pass
        try:
            publishers = BookPublisher.query.filter_by(book_id=self.id).all()
            for publisher in publishers:
                db.session.delete(publisher)
        except: pass
        try:
            formats = BookFormat.query.filter_by(book_id=self.id).all()
            for format in formats:
                db.session.delete(format)
        except: pass
        try:
            annotations = Annotation.query.filter_by(book_id=self.id).all()
            for annotation in annotations: 
                db.session.delete(annotation)
        except: pass
        try:
            reviews = Review.query.filter_by(book_id=self.id).all()
            for review in reviews: 
                db.session.delete(review)
        except: pass
        try:
            bucket = DeliveryBucket.query.filter_by(book_id=self.id).all()
            for book in bucket:
                book.delete()
        except: pass
        try:
            details = Detail.query.filter_by(book_id=self.id).all()
            for detail in details: 
                db.session.delete(detail)
        except: pass
        try:
            dumps = Dump.query.filter_by(book_id=self.id).all()
            for book in dumps: 
                db.session.delete(book)
        except: pass
        try:
            suggestions = Suggestion.query.filter_by(book_id=self.id).all()
            for book in suggestions: 
                db.session.delete(book)
        except: pass
        try:
            wishlists = Wishlist.query.filter_by(book_id=self.id).all()
            for book in wishlists: 
                db.session.delete(book)
        except: pass
        try:
            orders = Order.query.filter_by(book_id=self.id).all()
            for book in orders: 
                db.session.delete(book)
        except: pass
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_most_borrowed(age_group, start, end):
        if age_group:
            if age_group == 1:
                books = Book.query.filter_by(age_group_1=True, most_borrowed=True).order_by(Book.id.desc()).all()[start:end]
            elif age_group == 2:
                books = Book.query.filter_by(age_group_2=True, most_borrowed=True).order_by(Book.id.desc()).all()[start:end]
            elif age_group == 3:
                books = Book.query.filter_by(age_group_3=True, most_borrowed=True).order_by(Book.id.desc()).all()[start:end]
            elif age_group == 4:
                books = Book.query.filter_by(age_group_4=True, most_borrowed=True).order_by(Book.id.desc()).all()[start:end]
            elif age_group == 5:
                books = Book.query.filter_by(age_group_5=True, most_borrowed=True).order_by(Book.id.desc()).all()[start:end]
            elif age_group == 6:
                books = Book.query.filter_by(age_group_6=True, most_borrowed=True).order_by(Book.id.desc()).all()[start:end]
        else:
            books = Book.query.filter_by(most_borrowed=True).order_by(Book.id.desc()).all()[start:end]

        final_books = []
        for book in books:
            final_books.append(book.to_json())

        return final_books

    @staticmethod
    def get_bestsellers(age_group, start, end):
        if age_group:
            if age_group == 1:
                books = Book.query.filter_by(age_group_1=True, amazon_bestseller=True).all()[start:end]
            elif age_group == 2:
                books = Book.query.filter_by(age_group_2=True, amazon_bestseller=True).all()[start:end]
            elif age_group == 3:
                books = Book.query.filter_by(age_group_3=True, amazon_bestseller=True).all()[start:end]
            elif age_group == 4:
                books = Book.query.filter_by(age_group_4=True, amazon_bestseller=True).all()[start:end]
            elif age_group == 5:
                books = Book.query.filter_by(age_group_5=True, amazon_bestseller=True).all()[start:end]
            elif age_group == 6:
                books = Book.query.filter_by(age_group_6=True, amazon_bestseller=True).all()[start:end]
        else:
            books = Book.query.filter_by(amazon_bestseller=True).all()[start:end]

        final_books = []
        for book in books:
            final_books.append(book.to_json())

        return final_books

    @staticmethod
    def get_author_books(guid, start, end):
        from app.models.author import Author

        books = Author.query.filter_by(guid=guid).first().books[start:end]
        final_books = []

        for book in books:
            final_books.append(book.to_json())

        return final_books

    @staticmethod
    def get_publisher_books(guid, start, end):
        from app.models.publishers import Publisher

        books = Publisher.query.filter_by(guid=guid).first().books[start:end]
        final_books = []

        for book in books:
            final_books.append(book.to_json())

        return final_books

    @staticmethod
    def get_series_books(guid, start, end):
        from app.models.series import Series

        books = Series.query.filter_by(guid=guid).first().books[start:end]
        final_books = []

        for book in books:
            final_books.append(book.to_json())

        return final_books

    @staticmethod
    def get_type_books(guid, start, end):
        from app.models.format import Format

        books = Format.query.filter_by(guid=guid).first().books[start:end]
        final_books = []

        for book in books:
            final_books.append(book.to_json())

        return final_books

    @staticmethod
    def get_genres_books(guid):
        from app.models.category import Category

        books = Category.query.filter_by(guid=guid).first().books[:10]
        final_books = []

        for book in books:
            final_books.append(book.to_json())

        return final_books

    @staticmethod
    def get_similar_books(age_group):
        if age_group != "None":
            detail_objs = Detail.query.filter_by(age_group=age_group).order_by(Detail.bestseller_rank.asc()).limit(10).all()
            books = [Book.query.filter_by(id=obj.book_id).first() for obj in detail_objs]
        else:
            detail_objs = Detail.query.order_by(Detail.bestseller_rank.asc()).limit(10).all()
            books = [Book.query.filter_by(id=obj.book_id).first() for obj in detail_objs]
        return [book.to_json() for book in books]

    def to_json(self):
        return {
            "guid": self.guid,
            "isbn": self.isbn,
            "name": self.name,
            "image": self.image,
            "rating": self.rating,
            "review_count": self.review_count,
            "book_format": self.book_format,
            "language": self.language,
            "price": self.price,
            "description": self.description,
            "categories": [category.name for category in self.categories],
            "authors": [author.name for author in self.authors],
            "publishers": [publisher.name for publisher in self.publishers],
            "stock_available": self.stock_available,
            "rentals": self.rentals,
            "age_group_1": self.age_group_1,
            "age_group_2": self.age_group_2,
            "age_group_3": self.age_group_3,
            "age_group_4": self.age_group_4,
            "age_group_5": self.age_group_5,
            "age_group_6": self.age_group_6,
        }
