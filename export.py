from app.models.user import User, Address
import csv

from app import db

def export():
    users = User.query.all()

    master_csv = [
        [
            "id",
            "guid",
            "name",
            "age",
            "child_name",
            "mobile_number",
            "newsletter",
            "is_subscribed",
            "security_deposit",
            "customer_id",
            "plan_id",
            "subscription_id",
            "has_address",
            "address_id",
            "address_guid",
            "house_number",
            "area",
            "city",
            "pincode",
            "country",
            "landmark"
        ]
    ]

    for user in users:
        user_csv = []

        user_csv.append(user.id)
        user_csv.append(user.guid)
        user_csv.append(user.name)
        user_csv.append(user.age)
        user_csv.append(user.child_name)
        user_csv.append(user.mobile_number)
        user_csv.append(user.newsletter)
        user_csv.append(user.is_subscribed)
        user_csv.append(user.security_deposit)
        user_csv.append(user.customer_id)
        user_csv.append(user.plan_id)
        user_csv.append(user.subscription_id)

        #Create Cart and Wishlist for Users

        address = Address.query.filter_by(user_id=user.id).first()

        if address:
            user_csv.append("True")
            user_csv.append(address.id)
            user_csv.append(address.guid)
            user_csv.append(address.house_number)
            user_csv.append(address.area)
            user_csv.append(address.city)
            user_csv.append(address.pincode)
            user_csv.append(address.country)
            user_csv.append(address.landmark)
        else:
            user_csv.append("False")
            user_csv.append("")
            user_csv.append("")
            user_csv.append("")
            user_csv.append("")
            user_csv.append("")
            user_csv.append("")
            user_csv.append("")
            user_csv.append("")

        master_csv.append(user_csv)

    with open("data.csv", 'a+') as f:
        writer = csv.writer(f)
        for row in master_csv:
            writer.writerow(row)
        f.close()