from app import db
import uuid

from app.models.books import Book
from app.models.user import SeriesPreferences

class Series(db.Model):
    __tablename__ = "series"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    age1 = db.Column(db.Boolean, default=False)
    age2 = db.Column(db.Boolean, default=False)
    age3 = db.Column(db.Boolean, default=False)
    age4 = db.Column(db.Boolean, default=False)
    age5 = db.Column(db.Boolean, default=False)
    age6 = db.Column(db.Boolean, default=False)
    total_books = db.Column(db.Integer)
    books = db.relationship(Book, lazy=True)
    display = db.Column(db.Boolean, default=False)
    preferences = db.relationship('Preference', secondary=SeriesPreferences.__table__)

    @staticmethod
    def create(name, age1, age2, age3, age4, age5, age6, total_books, display):
        series_dict = dict(
            guid = str(uuid.uuid4()),
            name = name,
            age1 = age1,
            age2 = age2,
            age3 = age3,
            age4 = age4,
            age5 = age5,
            age6 = age6,
            total_books = total_books,
            display = display
        )
        series_obj = Series(**series_dict)
        db.session.add(series_obj)
        db.session.commit()

    @staticmethod
    def get_series(age_group):
        if age_group:
            if age_group == 1:
                series = Series.query.filter_by(age1=True).all()
            elif age_group == 2:
                series = Series.query.filter_by(age2=True).all()
            elif age_group == 3:
                series = Series.query.filter_by(age3=True).all()
            elif age_group == 4:
                series = Series.query.filter_by(age4=True).all()
            elif age_group == 5:
                series = Series.query.filter_by(age5=True).all()
            elif age_group == 6:
                series = Series.query.filter_by(age6=True).all()
        else:
            series = Series.query.filter_by(display=True).all()
        
        final_series = []
        for serie in series:
            final_series.append({
                "name": serie.name,
                "guid": serie.guid
            })

        return final_series

    @staticmethod
    def get_all_series(age_group):
        if age_group:
            if age_group == 1:
                series = Series.query.filter_by(age1=True).all()[10:]
            elif age_group == 2:
                series = Series.query.filter_by(age2=True).all()[10:]
            elif age_group == 3:
                series = Series.query.filter_by(age3=True).all()[10:]
            elif age_group == 4:
                series = Series.query.filter_by(age4=True).all()[10:]
            elif age_group == 5:
                series = Series.query.filter_by(age5=True).all()[10:]
            elif age_group == 6:
                series = Series.query.filter_by(age6=True).all()[10:]
        else:
            series = Series.query.filter_by(display=True).all()[10:]
        
        final_series = []
        for serie in series:
            final_series.append(serie.name)

        return final_series