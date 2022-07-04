from app import db
import uuid

class Annotation(db.Model):
    __tablename__ = "annotations"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    table_of_contents = db.Column(db.String)
    review_text = db.Column(db.String)
    review_quote = db.Column(db.String)
    flap_copy = db.Column(db.String)
    back_cover_copy = db.Column(db.String)
    about_author = db.Column(db.String)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)

    @staticmethod
    def create(table_of_contents, review_text, review_quote, flap_copy, back_cover_copy, about_author, book_id):
        annotation_dict = dict(
            guid = str(uuid.uuid4()),
            table_of_contents = table_of_contents,
            review_text = review_text,
            review_quote = review_quote,
            flap_copy = flap_copy,
            back_cover_copy = back_cover_copy,
            about_author = about_author,
            book_id = book_id
        )
        annotation_obj = Annotation(**annotation_dict)
        db.session.add(annotation_obj)
        db.session.commit()

    # def to_json(self):
    #     return {
    #         "about_title": self.about_title,
    #         "about_text": self.about_text,
    #         "review_text": self.review_text,
    #         "review_quote": self.review_quote
    #     }