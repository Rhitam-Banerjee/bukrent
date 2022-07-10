from app import db
import uuid

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    mobile_number = db.Column(db.String, unique=True)
    newsletter = db.Column(db.Boolean)
    is_subscribed = db.Column(db.Boolean, default=False)
    current_plan = db.Column(db.Integer)
    security_deposit = db.Column(db.Boolean, default=False)
    customer_id = db.Column(db.String)
    plan_id = db.Column(db.String)
    subscription_id = db.Column(db.String)
    #Cart
    #Wishlist
    #Subscription
    #Orders

    @staticmethod
    def create(first_name, last_name, mobile_number, newsletter):
        user_dict = dict(
            guid = str(uuid.uuid4()),
            first_name = first_name,
            last_name = last_name,
            mobile_number = mobile_number,
            newsletter = newsletter
        )
        user_obj = User(**user_dict)
        db.session.add(user_obj)
        db.session.commit()

    def add_subscription_details(self, plan, customer_id, plan_id, subscription_id):
        self.current_plan = plan
        self.customer_id = customer_id
        self.plan_id = plan_id
        self.subscription_id = subscription_id
        db.session.add(self)
        db.session.commit()