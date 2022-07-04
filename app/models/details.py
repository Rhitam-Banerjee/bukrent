from app import db
import uuid

from sqlalchemy.ext.hybrid import hybrid_property

class Detail(db.Model):
    __tablename__ = "details"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    age_group = db.Column(db.Integer)
    for_age = db.Column(db.String)
    pages = db.Column(db.String)
    language = db.Column(db.String)
    dimensions = db.Column(db.String)
    publisher = db.Column(db.String)
    publication_date = db.Column(db.String)
    bestseller_rank = db.Column(db.Integer)
    publication_location = db.Column(db.String)
    edition_statement = db.Column(db.String)
    edition = db.Column(db.String)
    imprint = db.Column(db.String)
    illustration_notes = db.Column(db.String)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)

    @hybrid_property
    def display_age_group(self):
        if self.age_group == 1:
            return "0-2"
        elif self.age_group == 2:
            return "3-5"
        elif self.age_group == 3:
            return "6-8"
        elif self.age_group == 4:
            return "9-11"
        elif self.age_group == 5:
            return "12+"

    @staticmethod
    def get_age_bracket(group):
        if group == "1":
            return "0-2"
        elif group == "2":
            return "3-5"
        elif group == "3":
            return "6-8"
        elif group == "4":
            return "9-11"
        elif group == "5":
            return "12-14"
        else:
            return "15+"

    @staticmethod
    def create(age_group, for_age, pages, language, dimensions, publisher, publication_date, bestseller_rank, publication_location, edition_statement, edition, imprint, illustration_notes, book_id):
        detail_dict = dict(
            guid = str(uuid.uuid4()),
            age_group = age_group,
            for_age = for_age,
            pages = pages,
            language = language,
            dimensions = dimensions,
            publisher = publisher,
            publication_date = publication_date,
            bestseller_rank = bestseller_rank,
            publication_location = publication_location,
            edition_statement = edition_statement,
            edition = edition,
            imprint = imprint,
            illustration_notes = illustration_notes,
            book_id = book_id
        )

        detail_obj = Detail(**detail_dict)
        db.session.add(detail_obj)
        db.session.commit()

    @staticmethod
    def get_bestsellers():
        objs = Detail.query.order_by(Detail.bestseller_rank.asc()).limit(10).all()
        return [obj.book_id for obj in objs]

    @staticmethod
    def get_bestsellers_for_age(age_group):
        if age_group == "1":
            objs = Detail.query.filter_by(age_group=1).order_by(Detail.bestseller_rank.asc()).limit(10).all()
        elif age_group == "2":
            objs = Detail.query.filter_by(age_group=2).order_by(Detail.bestseller_rank.asc()).limit(10).all()
        elif age_group == "3":
            objs = Detail.query.filter_by(age_group=3).order_by(Detail.bestseller_rank.asc()).limit(10).all()
        elif age_group == "4":
            objs = Detail.query.filter_by(age_group=4).order_by(Detail.bestseller_rank.asc()).limit(10).all()
        else:
            objs = Detail.query.filter_by(age_group=5).order_by(Detail.bestseller_rank.asc()).limit(10).all()
        return [obj.book_id for obj in objs]

    # def to_json(self):
    #     age_group = "Unknown"
    #     if self.age_group1:
    #         age_group = "0-2"
    #     elif self.age_group2:
    #         age_group = "3-5"
    #     elif self.age_group3:
    #         age_group = "6-8"
    #     elif self.age_group4:
    #         age_group = "9-11"
    #     elif self.age_group5:
    #         age_group = "12-14"
    #     elif self.age_group6:
    #         age_group = "15+"
    #     return {
    #         "age_group": age_group,
    #         "for_age": self.for_age,
    #         "pages": self.pages,
    #         "language": self.language,
    #         "dimensions": self.dimensions,
    #         "publisher": self.publisher,
    #         "publication_date": self.publication_date,
    #         "bestseller_rank": self.bestseller_rank,
    #         "publication_location": self.publication_location,
    #         "edition_statement": self.edition_statement,
    #         "edition": self.edition,
    #         "imprint": self.imprint,
    #         "illustration_notes": self.illustration_notes
    #     }