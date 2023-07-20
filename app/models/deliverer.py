from app import db

class Deliverer(db.Model):
    __tablename__ = "deliverers"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    mobile_number = db.Column(db.String)

    @staticmethod
    def create(firstname, lastname, username, password, mobile_number):
        deliverer_dict = dict(
            first_name=firstname,
            last_name=lastname,
            password=password,
            username=username,
            mobile_number=mobile_number
        )
        deliverer_obj = Deliverer(**deliverer_dict)
        db.session.add(deliverer_obj)
        db.session.commit()

        return deliverer_obj

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "mobile_number": self.mobile_number,
        }
