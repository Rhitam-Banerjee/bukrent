from app import db
import uuid

class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    review = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)

    @staticmethod
    def create(review, author, book_id):
        review_dict = dict(
            guid = str(uuid.uuid4()),
            review = review,
            author = author,
            book_id = book_id
        )
        review_obj = Review(**review_dict)
        db.session.add(review_obj)
        db.session.commit()

    # def to_json(self):
    #     return {
    #         "review": self.review,
    #         "author": sekf.author
    #     }