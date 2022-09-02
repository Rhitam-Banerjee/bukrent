from app import db
import uuid

from app.models.books import BookAuthor
from app.models.user import AuthorPreferences

from sqlalchemy import or_

class Author(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False, unique=True)
    author_type = db.Column(db.String)
    age1 = db.Column(db.Boolean, default=False)
    age2 = db.Column(db.Boolean, default=False)
    age3 = db.Column(db.Boolean, default=False)
    age4 = db.Column(db.Boolean, default=False)
    age5 = db.Column(db.Boolean, default=False)
    age6 = db.Column(db.Boolean, default=False)
    total_books = db.Column(db.Integer)
    display = db.Column(db.Boolean, default=False)
    books = db.relationship('Book', secondary=BookAuthor.__table__)
    preferences = db.relationship('Preference', secondary=AuthorPreferences.__table__)

    @staticmethod
    def create(name, author_type, age1, age2, age3, age4, age5, age6, total_books, display):
        author_dict = dict(
            guid = str(uuid.uuid4()),
            name = name,
            author_type = author_type,
            age1 = age1,
            age2 = age2,
            age3 = age3,
            age4 = age4,
            age5 = age5,
            age6 = age6,
            total_books = total_books,
            display = display
        )
        author_obj = Author(**author_dict)
        db.session.add(author_obj)
        db.session.commit()

    @staticmethod
    def get_authors(age_group):
        if age_group:
            if age_group == 1:
                authors = Author.query.filter_by(age1=True).all()
            elif age_group == 2:
                authors = Author.query.filter_by(age2=True).all()
            elif age_group == 3:
                authors = Author.query.filter_by(age3=True).all()
            elif age_group == 4:
                authors = Author.query.filter_by(age4=True).all()
            elif age_group == 5:
                authors = Author.query.filter_by(age5=True).all()
            elif age_group == 6:
                authors = Author.query.filter_by(age6=True).all()
        else:
            authors = Author.query.filter(or_(
                Author.age1==True,
                Author.age2==True,
                Author.age3==True,
                Author.age4==True,
                Author.age5==True,
                Author.age6==True
            )).all()
        
        final_authors = []
        for author in authors:
            final_authors.append({
                "name": author.name,
                "guid": author.guid
            })

        return final_authors