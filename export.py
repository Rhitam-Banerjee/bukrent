from app.models.user import User, Address, Child
import csv

from app import db

def export():
    ########################### Users
    users = User.query.all()

    master_csv = [
        [
            "id",
            "guid",
            "first_name",
            "last_name",
            "mobile_number",
            "email",
            "newsletter",
            "is_subscribed",
            "security_deposit",
            "payment_id",
            "plan_id",
            "subscription_id",
            "order_id"
        ]
    ]

    for user in users:
        user_csv = []

        user_csv.append(user.id)
        user_csv.append(user.guid)
        user_csv.append(user.first_name)
        user_csv.append(user.last_name)
        user_csv.append(user.mobile_number)
        user_csv.append(user.email)
        user_csv.append(user.newsletter)
        user_csv.append(user.is_subscribed)
        user_csv.append(user.security_deposit)
        user_csv.append(user.payment_id)
        user_csv.append(user.plan_id)
        user_csv.append(user.subscription_id)
        user_csv.append(user.order_id)

        master_csv.append(user_csv)

    with open("export_data/users.csv", 'a+') as f:
        writer = csv.writer(f)
        for row in master_csv:
            writer.writerow(row)
        f.close()

    ########################### Address
    addresses = Address.query.all()

    master_csv = [
        [
            "id",
            "guid",
            "house_number",
            "building",
            "area",
            "pincode",
            "landmark",
            "user_id"
        ]
    ]

    for address in addresses:
        address_csv = []

        address_csv.append(address.id)
        address_csv.append(address.guid)
        address_csv.append(address.first_name)
        address_csv.append(address.last_name)
        address_csv.append(address.mobile_number)
        address_csv.append(address.email)
        address_csv.append(address.newsletter)
        address_csv.append(address.is_subscribed)
        address_csv.append(address.security_deposit)
        address_csv.append(address.payment_id)
        address_csv.append(address.plan_id)
        address_csv.append(address.subscription_id)
        address_csv.append(address.order_id)

        master_csv.append(address_csv)

    with open("export_data/address.csv", 'a+') as f:
        writer = csv.writer(f)
        for row in master_csv:
            writer.writerow(row)
        f.close()

    ########################### Child
    children = Child.query.all()

    master_csv = [
        [
            "id",
            "guid",
            "name",
            "dob",
            "age_group",
            "user_id"
        ]
    ]

    for child in children:
        child_csv = []

        child_csv.append(child.id)
        child_csv.append(child.guid)
        child_csv.append(child.first_name)
        child_csv.append(child.last_name)
        child_csv.append(child.mobile_number)
        child_csv.append(child.email)
        child_csv.append(child.newsletter)
        child_csv.append(child.is_subscribed)
        child_csv.append(child.security_deposit)
        child_csv.append(child.payment_id)
        child_csv.append(child.plan_id)
        child_csv.append(child.subscription_id)
        child_csv.append(child.order_id)

        master_csv.append(child_csv)

    with open("export_data/child.csv", 'a+') as f:
        writer = csv.writer(f)
        for row in master_csv:
            writer.writerow(row)
        f.close()