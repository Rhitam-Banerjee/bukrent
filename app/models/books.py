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
    stock_available = db.Column(db.Integer)

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
            stock_available = stock_available
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

    @staticmethod
    def get_most_borrowed(age_group):
        if age_group:
            if age_group == 1:
                books = Book.query.filter_by(borrowed_age1=True).order_by(Book.id.desc()).all()[:10]
            elif age_group == 2:
                books = Book.query.filter_by(borrowed_age2=True).order_by(Book.id.desc()).all()[:10]
            elif age_group == 3:
                books = Book.query.filter_by(borrowed_age3=True).order_by(Book.id.desc()).all()[:10]
            elif age_group == 4:
                books = Book.query.filter_by(borrowed_age4=True).order_by(Book.id.desc()).all()[:10]
            elif age_group == 5:
                books = Book.query.filter_by(borrowed_age5=True).order_by(Book.id.desc()).all()[:10]
            elif age_group == 6:
                books = Book.query.filter_by(borrowed_age6=True).order_by(Book.id.desc()).all()[:10]
        else:
            books = Book.query.filter_by(most_borrowed=True).order_by(Book.id.desc()).all()[:10]
        
        final_books = []
        for book in books:
            final_books.append(book.to_json())

        return final_books

    @staticmethod
    def get_all_most_borrowed(age_group):
        if age_group:
            if age_group == 1:
                books = Book.query.filter_by(borrowed_age1=True).order_by(Book.id.desc()).all()[10:]
            elif age_group == 2:
                books = Book.query.filter_by(borrowed_age2=True).order_by(Book.id.desc()).all()[10:]
            elif age_group == 3:
                books = Book.query.filter_by(borrowed_age3=True).order_by(Book.id.desc()).all()[10:]
            elif age_group == 4:
                books = Book.query.filter_by(borrowed_age4=True).order_by(Book.id.desc()).all()[10:]
            elif age_group == 5:
                books = Book.query.filter_by(borrowed_age5=True).order_by(Book.id.desc()).all()[10:]
            elif age_group == 6:
                books = Book.query.filter_by(borrowed_age6=True).order_by(Book.id.desc()).all()[10:]
        else:
            books = Book.query.filter_by(most_borrowed=True).order_by(Book.id.desc()).all()[10:]
        
        final_books = []
        for book in books:
            final_books.append(book.to_json())

        return final_books

    @staticmethod
    def get_author_books(author):
        from app.models.author import Author

        books = Author.query.filter_by(name=author).first().books[:10]
        final_books = []

        for book in books:
            final_books.append(book.to_json())

        return final_books

    @staticmethod
    def get_publisher_books(publisher):
        from app.models.publishers import Publisher

        books = Publisher.query.filter_by(name=publisher).first().books[:10]
        final_books = []

        for book in books:
            final_books.append(book.to_json())

        return final_books

    @staticmethod
    def get_series_books(series):
        from app.models.series import Series

        books = Series.query.filter_by(name=series).first().books
        final_books = []

        for book in books:
            final_books.append(book.to_json())

        return final_books

    @staticmethod
    def get_genres_books(genres):
        from app.models.category import Category

        books = Category.query.filter_by(name=genres).first().books[:10]
        final_books = []

        for book in books:
            final_books.append(book.to_json())

        return final_books

    @staticmethod
    def get_amazon_bestsellers(age_group):
        if age_group:
            if age_group == 1:
                books = Book.query.filter_by(bestseller_age1=True).all()[:10]
            elif age_group == 2:
                books = Book.query.filter_by(bestseller_age2=True).all()[:10]
            elif age_group == 3:
                books = Book.query.filter_by(bestseller_age3=True).all()[:10]
            elif age_group == 4:
                books = Book.query.filter_by(bestseller_age4=True).all()[:10]
            elif age_group == 5:
                books = Book.query.filter_by(bestseller_age5=True).all()[:10]
            elif age_group == 6:
                books = Book.query.filter_by(bestseller_age6=True).all()[:10]
        else:
            books = Book.query.filter_by(amazon_bestseller=True).all()[:10]
        
        final_books = []
        for book in books:
            final_books.append(book.to_json())

        return final_books

    @staticmethod
    def get_all_amazon_bestsellers(age_group):
        if age_group:
            if age_group == 1:
                books = Book.query.filter_by(bestseller_age1=True).all()[10:]
            elif age_group == 2:
                books = Book.query.filter_by(bestseller_age2=True).all()[10:]
            elif age_group == 3:
                books = Book.query.filter_by(bestseller_age3=True).all()[10:]
            elif age_group == 4:
                books = Book.query.filter_by(bestseller_age4=True).all()[10:]
            elif age_group == 5:
                books = Book.query.filter_by(bestseller_age5=True).all()[10:]
            elif age_group == 6:
                books = Book.query.filter_by(bestseller_age6=True).all()[10:]
        else:
            books = Book.query.filter_by(amazon_bestseller=True).all()[10:]
        
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
            "publishers": [publisher.name for publisher in self.publishers]
        }