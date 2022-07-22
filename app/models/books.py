from app import db
import uuid

from app.models.annotations import Annotation
from app.models.reviews import Review
from app.models.details import Detail

from app.models.cart import CartBook, WishlistBook
from app.models.order import OrderBook

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

    carts = db.relationship('Cart', secondary=CartBook.__table__)
    wishlists = db.relationship('Wishlist', secondary=WishlistBook.__table__)
    orders = db.relationship('Order', secondary=OrderBook.__table__)

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
    def get_most_borrowed(age_group):
        from app.models.category import Category

        if age_group:
            if age_group == 1:
                books = Category.query.filter_by(name="Zero - Two").first().books
            elif age_group == 2:
                books = Category.query.filter_by(name="Three to Five").first().books
            elif age_group == 3:
                books = Category.query.filter_by(name="Six to Eight").first().books
            elif age_group == 4:
                books = Category.query.filter_by(name="Nine to Twelve").first().books
            elif age_group == 5 or age_group == 6:
                books = Category.query.filter_by(name="Twelve to Sixteen").first().books
            category = Category.query.filter_by(name="Most Borrowed").first()

            final_books = []
            for book in books:
                if category in book.categories:
                    final_books.append(book.to_json())

        else:
            books = Category.query.filter_by(name="Most Borrowed").first().books[:10]
            final_books = []
            for book in books:
                final_books.append(book.to_json())

        return final_books

    @staticmethod
    def get_all_most_borrowed(age_group):
        from app.models.category import Category

        if not age_group:
            books = Category.query.filter_by(name="Most Borrowed").first().books[10:]
            final_books = []
            for book in books:
                final_books.append(book.to_json())
        else:
            return []
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
        from app.models.category import Category

        books = Category.query.filter_by(name="Amazon Bestseller").first().books[:10]
        final_books = []

        if age_group == 1:
            books = Category.query.filter_by(name="Zero - Two").first().books[:10]
        elif age_group == 2:
            books = Category.query.filter_by(name="Three to Five").first().books[:10]
        elif age_group == 3:
            books = Category.query.filter_by(name="Six to Eight").first().books[:10]
        elif age_group == 4:
            books = Category.query.filter_by(name="Nine to Twelve").first().books[:10]
        elif age_group == 5 or age_group == 6:
            books = Category.query.filter_by(name="Twelve to Sixteen").first().books[:10]

        for book in books:
            final_books.append(book.to_json())

        return final_books

    @staticmethod
    def get_all_amazon_bestsellers(age_group):
        from app.models.category import Category

        books = Category.query.filter_by(name="Amazon Bestseller").first().books[10:]
        final_books = []

        if age_group == 1:
            books = Category.query.filter_by(name="Zero - Two").first().books[10:]
        elif age_group == 2:
            books = Category.query.filter_by(name="Three to Five").first().books[10:]
        elif age_group == 3:
            books = Category.query.filter_by(name="Six to Eight").first().books[10:]
        elif age_group == 4:
            books = Category.query.filter_by(name="Nine to Twelve").first().books[10:]
        elif age_group == 5 or age_group == 6:
            books = Category.query.filter_by(name="Twelve to Sixteen").first().books[10:]

        for book in books:
            final_books.append(book.to_json())

        return final_books

    @staticmethod
    def get_more_books(detail):
        objs = Detail.query.filter_by(age_group=detail.age_group).order_by(Detail.bestseller_rank.asc()).limit(10).all()
        return [Book.query.filter_by(id=obj.book_id).first() for obj in objs]

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