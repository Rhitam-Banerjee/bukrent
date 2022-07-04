from app import db
import uuid

from sqlalchemy.sql.expression import func

from app.models.books import BookAuthor

class Author(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False, unique=True)
    author_type = db.Column(db.String)
    age1_books = db.Column(db.Integer)
    age2_books = db.Column(db.Integer)
    age3_books = db.Column(db.Integer)
    age4_books = db.Column(db.Integer)
    age5_books = db.Column(db.Integer)
    total_books = db.Column(db.Integer)
    books = db.relationship('Book', secondary=BookAuthor.__table__)
    display = db.Column(db.Boolean, default=False)

    @staticmethod
    def create(name, author_type, age1_books, age2_books, age3_books, age4_books, age5_books, total_books):
        author_dict = dict(
            guid = str(uuid.uuid4()),
            name = name,
            author_type = author_type,
            age1_books = age1_books,
            age2_books = age2_books,
            age3_books = age3_books,
            age4_books = age4_books,
            age5_books = age5_books,
            total_books = total_books
        )
        author_obj = Author(**author_dict)
        db.session.add(author_obj)
        db.session.commit()

    @staticmethod
    def get_top_authors():
        return Author.query.order_by(Author.total_books.desc()).limit(10).all()

    # @staticmethod
    # def get_top_authors():
    #     objs = db.session.query(func.count(Author.books) > 0).limit(10).all()
    #     # authors = []
    #     # for obj in objs:
    #     #     if len(obj.books) < 3:
    #     #         continue
    #     #     temp_dict = {}
    #     #     temp_dict["name"] = obj.name
    #     #     temp_dict["guid"] = obj.guid
    #     #     temp_dict["objs"] = obj.books
    #     #     authors.append(temp_dict)
    #     # return authors
    #     return objs