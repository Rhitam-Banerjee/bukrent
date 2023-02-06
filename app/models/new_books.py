from app import db
import uuid

class NewBook(db.Model): 
    __tablename__ = 'new_books'
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    isbn = db.Column(db.String, nullable=False)
    rating = db.Column(db.String)
    review_count = db.Column(db.String)
    category = db.Column(db.String, nullable=False)
    book_order = db.Column(db.Integer)
    category_order = db.Column(db.Integer)
    min_age = db.Column(db.Integer)
    max_age = db.Column(db.Integer)

    @staticmethod
    def create(name, image, isbn, rating, review_count, category, book_order, category_order, min_age, max_age):
        book_dict = dict(
            guid = str(uuid.uuid4()),
            name = name,
            image = image,
            isbn = isbn,
            rating = rating,
            review_count = review_count,
            category = category,
            book_order = book_order,
            category_order = category_order,
            min_age = min_age,
            max_age = max_age
        )

        new_book_obj = NewBook(**book_dict)
        db.session.add(new_book_obj)
        db.session.commit()

    def to_json(self): 
        return {
            "id": self.id,
            "guid": self.guid,
            "name": self.name,
            "image": self.image,
            "isbn": self.isbn,
            "rating": self.rating,
            "review_count": self.review_count,
            "book_order": self.book_order
        }