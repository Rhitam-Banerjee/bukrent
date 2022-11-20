from app import db
import uuid

from app.models.books import BookFormat
from app.models.user import FormatPreferences

class Format(db.Model):
    __tablename__ = "formats"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False, unique=True)
    age1 = db.Column(db.Boolean, default=False)
    age2 = db.Column(db.Boolean, default=False)
    age3 = db.Column(db.Boolean, default=False)
    age4 = db.Column(db.Boolean, default=False)
    age5 = db.Column(db.Boolean, default=False)
    age6 = db.Column(db.Boolean, default=False)
    total_books = db.Column(db.Integer)
    display = db.Column(db.Boolean, default=False)
    books = db.relationship('Book', secondary=BookFormat.__table__)
    preferences = db.relationship('Preference', secondary=FormatPreferences.__table__)

    @staticmethod
    def create(name, age1, age2, age3, age4, age5, age6, total_books, display):
        format_dict = dict(
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
        format_obj = Format(**format_dict)
        db.session.add(format_obj)
        db.session.commit()

    @staticmethod
    def get_types(age_group, start, end):
        if age_group:
            if age_group == 1:
                types = Format.query.filter_by(age1=True).all()[start:end]
            elif age_group == 2:
                types = Format.query.filter_by(age2=True).all()[start:end]
            elif age_group == 3:
                types = Format.query.filter_by(age3=True).all()[start:end]
            elif age_group == 4:
                types = Format.query.filter_by(age4=True).all()[start:end]
            elif age_group == 5:
                types = Format.query.filter_by(age5=True).all()[start:end]
            elif age_group == 6:
                types = Format.query.filter_by(age6=True).all()[start:end]
        else:
            types = Format.query.filter(or_(
                Format.age1==True,
                Format.age2==True,
                Format.age3==True,
                Format.age4==True,
                Format.age5==True,
                Format.age6==True
            )).all()[start:end]

        final_types = []
        for format_obj in types:
            final_types.append({
                "name": format_obj.name,
                "guid": format_obj.guid
            })

        return final_types

    def to_json(self):
        return {
            "name": self.name,
            "guid": self.guid
        }
