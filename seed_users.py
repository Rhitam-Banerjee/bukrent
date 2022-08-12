import csv

from app import db

from app.models.user import *

def seed_users(): #Needs to change based on new export script
    print("Seeding Users")
    users = []
    with open("export_data/users.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            users.append(line)

    users = users[1:]

    addresses = []
    with open("export_data/address.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            addresses.append(line)

    addresses = addresses[1:]

    children = []
    with open("export_data/child.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            children.append(line)

    children = children[1:]

    final_data = {}

    for user in users:
        final_data[user[0]] = {
            "user_data": {
                "guid": user[1],
                "first_name": user[2],
                "last_name": user[3],
                "mobile_number": user[4],
                "email": user[5],
                "password": user[6],
                "newsletter": user[7],
                "is_subscribed": user[8],
                "security_deposit": user[9],
                "payment_id": user[10],
                "plan_id": user[11],
                "subscription_id": user[12],
                "order_id": user[13]
            },
            "address_data": {},
            "child_data": []
        }

    for address in addresses:
        final_data[address[7]]["address_data"]["guid"] = address[1]
        final_data[address[7]]["address_data"]["house_number"] = address[2]
        final_data[address[7]]["address_data"]["building"] = address[3]
        final_data[address[7]]["address_data"]["area"] = address[4]
        final_data[address[7]]["address_data"]["pincode"] = address[5]
        final_data[address[7]]["address_data"]["landmark"] = address[6]

    for child in children:
        final_data[child[5]]["child_data"].append(
            {
                "guid": child[1],
                "name": child[2],
                "dob": child[3],
                "age_group": child[4]
            }
        )

    for user_id, master_data in final_data.items():
        user_obj = User(
            guid=master_data["user_data"]["guid"],
            first_name=master_data["user_data"]["first_name"],
            last_name=master_data["user_data"]["last_name"],
            mobile_number=master_data["user_data"]["mobile_number"],
            email=master_data["user_data"]["email"],
            password=master_data["user_data"]["password"],
            newsletter=True if master_data["user_data"]["newsletter"] == "True" else False,
            is_subscribed=True if master_data["user_data"]["is_subscribed"] == "True" else False,
            security_deposit=True if master_data["user_data"]["security_deposit"] == "True" else False,
            payment_id=master_data["user_data"]["payment_id"],
            plan_id=master_data["user_data"]["plan_id"],
            subscription_id=master_data["user_data"]["subscription_id"],
            order_id=master_data["user_data"]["order_id"]
        )

        db.session.add(user_obj)
        db.session.commit()

        if master_data["address_data"].get("guid"):
            address_obj = Address(
                guid=master_data["address_data"]["guid"],
                house_number=master_data["address_data"]["house_number"],
                building=master_data["address_data"]["building"],
                area=master_data["address_data"]["area"],
                pincode=master_data["address_data"]["pincode"],
                landmark=master_data["address_data"]["landmark"],
                user_id=user_obj.id
            )

            db.session.add(address_obj)
            db.session.commit()

        for child_dict in master_data["child_data"]:
            child_obj = Child(
                guid=child_dict.get("guid"),
                name=child_dict.get("name"),
                dob=child_dict.get("dob"),
                age_group=child_dict.get("age_group"),
                user_id=user_obj.id
            )
            db.session.add(child_obj)
            db.session.commit()