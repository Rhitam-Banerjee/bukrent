from app import db
import uuid

class Search(db.Model):
    __tablename__ = "search"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    mobile_number = db.Column(db.String, nullable=False)
    book_name = db.Column(db.String, nullable=False)
    book_link = db.Column(db.String, nullable=False)

    @staticmethod
    def create(name, mobile_number, book_name, book_link):
        search_dict = dict(
            guid = str(uuid.uuid4()),
            name = name,
            mobile_number = mobile_number,
            book_name = book_name,
            book_link = book_link
        )
        search_obj = Search(**search_dict)
        db.session.add(search_obj)
        db.session.commit()