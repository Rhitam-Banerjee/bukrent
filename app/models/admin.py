from app import db
import uuid

class Admin(db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username
        }
