import csv

from app import db

from app.models.user import *
from app.models.category import Category
from app.models.author import Author
from app.models.series import Series
from app.models.format import Format

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

    preferences = []
    with open("export_data/preference.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            preferences.append(line)

    preferences = preferences[1:]

    final_data = {}

    for user in users:
        final_data[user[0]] = {
            "user_data": {
                "guid": user[1],
                "first_name": user[2],
                "last_name": user[3],
                "mobile_number": user[4],
                "created_at": user[5],
                "email": user[6],
                "password": user[7],
                "newsletter": user[8],
                "is_subscribed": user[9],
                "security_deposit": user[10],
                "payment_id": user[11],
                "plan_id": user[12],
                "subscription_id": user[13],
                "order_id": user[14]
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
        preference_dict = {}
        for preference in preferences:
            if child[0] ==  preference[10]:
                categories = preference[6].strip('][').replace("'", "").split(", ")
                formats = preference[7].strip('][').replace("'", "").split(", ")
                authors = preference[8].strip('][').replace("'", "").split(", ")
                series = preference[9].strip('][').replace("'", "").split(", ")

                if not categories[0]:
                    categories = []
                if not formats[0]:
                    formats = []
                if not authors[0]:
                    authors = []
                if not series[0]:
                    series = []

                preference_dict["guid"] = preference[1]
                preference_dict["last_book_read1"] = preference[2]
                preference_dict["last_book_read2"] = preference[3]
                preference_dict["last_book_read3"] = preference[4]
                preference_dict["books_read_per_week"] = preference[5]
                preference_dict["categories"] = categories
                preference_dict["formats"] = formats
                preference_dict["authors"] = authors
                preference_dict["series"] = series
        final_data[child[5]]["child_data"].append(
            {
                "guid": child[1],
                "name": child[2],
                "dob": child[3],
                "age_group": child[4],
                "preferences": preference_dict
            }
        )

    for user_obj_id, master_data in final_data.items():
        user_obj = User(
            guid=master_data["user_data"]["guid"],
            first_name=master_data["user_data"]["first_name"],
            last_name=master_data["user_data"]["last_name"],
            mobile_number=master_data["user_data"]["mobile_number"],
            email=master_data["user_data"]["email"],
            password=master_data["user_data"]["password"],
            created_at=master_data["user_data"]["created_at"],
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

        age_groups = []

        for child_dict in master_data["child_data"]:
            age_groups.append(int(child_dict.get("age_group")))
            child_obj = Child(
                guid=child_dict.get("guid"),
                name=child_dict.get("name"),
                dob=child_dict.get("dob"),
                age_group=child_dict.get("age_group"),
                user_id=user_obj.id
            )
            db.session.add(child_obj)
            db.session.commit()

            preferences = child_dict.get("preferences")
            if preferences.get("guid"):
                books_read_per_week = 0
                if preferences.get("books_read_per_week"):
                    books_read_per_week = preferences.get("books_read_per_week")
                preference_obj = Preference(
                    guid=preferences.get("guid"),
                    last_book_read1=preferences.get("last_book_read1"),
                    last_book_read2=preferences.get("last_book_read2"),
                    last_book_read3=preferences.get("last_book_read3"),
                    books_read_per_week=books_read_per_week,
                    categories=[Category.query.filter_by(name=category).first() for category in preferences.get("categories")],
                    formats=[Format.query.filter_by(name=format_obj).first() for format_obj in preferences.get("formats")],
                    authors=[Author.query.filter_by(name=author).first() for author in preferences.get("authors")],
                    series=[Series.query.filter_by(name=series).first() for series in preferences.get("series")],
                    child_id=child_obj.id
                )

                db.session.add(preference_obj)
                db.session.commit()

        user_obj.add_age_groups(age_groups)