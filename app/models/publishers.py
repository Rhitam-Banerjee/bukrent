from app import db
import uuid

from app.models.books import BookPublisher

class Publisher(db.Model):
    __tablename__ = "publishers"
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
    display = db.Column(db.Boolean, default=False)
    books = db.relationship('Book', secondary=BookPublisher.__table__)

    @staticmethod
    def create(name, age1, age2, age3, age4, age5, age6, total_books, display):
        publisher_dict = dict(
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
        publisher_obj = Publisher(**publisher_dict)
        db.session.add(publisher_obj)
        db.session.commit()

    @staticmethod
    def get_publishers(age_group, start, end):
        if age_group:
            if age_group == 1:
                publishers = Publisher.query.filter_by(age1=True).all()[start:end]
            elif age_group == 2:
                publishers = Publisher.query.filter_by(age2=True).all()[start:end]
            elif age_group == 3:
                publishers = Publisher.query.filter_by(age3=True).all()[start:end]
            elif age_group == 4:
                publishers = Publisher.query.filter_by(age4=True).all()[start:end]
            elif age_group == 5:
                publishers = Publisher.query.filter_by(age5=True).all()[start:end]
            elif age_group == 6:
                publishers = Publisher.query.filter_by(age6=True).all()[start:end]
        else:
            publishers = Publisher.query.filter(or_(
                Publisher.age1==True,
                Publisher.age2==True,
                Publisher.age3==True,
                Publisher.age4==True,
                Publisher.age5==True,
                Publisher.age6==True
            )).all()[start:end]
        
        final_publishers = []
        for publisher in publishers:
            final_publishers.append({
                "name": publisher.name,
                "guid": publisher.guid
            })

        return final_publishers