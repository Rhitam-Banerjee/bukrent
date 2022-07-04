from app import db
import uuid

class Launch(db.Model):
    __tablename__ = "launch"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    parent_name = db.Column(db.String, nullable=False)
    mobile_number = db.Column(db.String, nullable=False)
    child_name = db.Column(db.String, nullable=False)
    age_group = db.Column(db.String, nullable=False)

    @staticmethod
    def create(parent_name, mobile_number, child_name, age_group):
        launch_dict = dict(
            guid = str(uuid.uuid4()),
            parent_name = parent_name,
            mobile_number = mobile_number,
            child_name = child_name,
            age_group = age_group
        )
        launch_obj = Launch(**launch_dict)
        db.session.add(launch_obj)
        db.session.commit()