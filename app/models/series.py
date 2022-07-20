from app import db
import uuid

from app.models.books import Book

class Series(db.Model):
    __tablename__ = "series"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    age1_books = db.Column(db.Integer)
    age2_books = db.Column(db.Integer)
    age3_books = db.Column(db.Integer)
    age4_books = db.Column(db.Integer)
    age5_books = db.Column(db.Integer)
    total_books = db.Column(db.Integer)
    books = db.relationship(Book, lazy=True)
    display = db.Column(db.Boolean, default=False)

    @staticmethod
    def create(name, age1_books, age2_books, age3_books, age4_books, age5_books, total_books):
        series_dict = dict(
            guid = str(uuid.uuid4()),
            name = name,
            age1_books = age1_books,
            age2_books = age2_books,
            age3_books = age3_books,
            age4_books = age4_books,
            age5_books = age5_books,
            total_books = total_books
        )
        series_obj = Series(**series_dict)
        db.session.add(series_obj)
        db.session.commit()

    @staticmethod
    def get_series(age_group):
        if age_group:
            if age_group == 1:
                series = Series.query.order_by(Series.age1_books.desc()).limit(10).all()
            elif age_group == 2:
                series = Series.query.order_by(Series.age2_books.desc()).limit(10).all()
            elif age_group == 3:
                series = Series.query.order_by(Series.age3_books.desc()).limit(10).all()
            elif age_group == 4:
                series = Series.query.order_by(Series.age4_books.desc()).limit(10).all()
            else:
                series = Series.query.order_by(Series.age5_books.desc()).limit(10).all()
        else:
            series = Series.query.order_by(Series.total_books.desc()).limit(10).all()
        return [serie.name for serie in series]

    # @staticmethod
    # def get_top_series():
    #     return Series.query.order_by(Series.total_books.desc()).limit(10).all()

    # @staticmethod
    # def get_top_series():
    #     objs = Series.query.all()
    #     series = []
    #     for obj in objs:
    #         if len(obj.books) < 3:
    #             continue
    #         temp_dict = {}
    #         temp_dict["name"] = obj.name
    #         temp_dict["guid"] = obj.guid
    #         temp_dict["books"] = len(obj.books)
    #         temp_dict["objs"] = obj.books
    #         series.append(temp_dict)
    #     return series