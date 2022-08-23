from app.models.user import User, Address, Child, Preference
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
            "created_at",
            "email",
            "password",
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
        user_csv.append(user.created_at)
        user_csv.append(user.email)
        user_csv.append(user.password)
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
        address_csv.append(address.house_number)
        address_csv.append(address.building)
        address_csv.append(address.area)
        address_csv.append(address.pincode)
        address_csv.append(address.landmark)
        address_csv.append(address.user_id)

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
        child_csv.append(child.name)
        child_csv.append(child.dob)
        child_csv.append(child.age_group)
        child_csv.append(child.user_id)

        master_csv.append(child_csv)

    with open("export_data/child.csv", 'a+') as f:
        writer = csv.writer(f)
        for row in master_csv:
            writer.writerow(row)
        f.close()

    ########################### Preferences
    preferences = Preference.query.all()

    master_csv = [
        [
            "id",
            "guid",
            "last_book_read1",
            "last_book_read2",
            "last_book_read3",
            "books_read_per_week",
            "categories",
            "formats",
            "authors",
            "series",
            "child_id"
        ]
    ]

    for preference in preferences:
        preference_csv = []

        preference_csv.append(preference.id)
        preference_csv.append(preference.guid)
        preference_csv.append(preference.last_book_read1)
        preference_csv.append(preference.last_book_read2)
        preference_csv.append(preference.last_book_read3)
        preference_csv.append(preference.books_read_per_week)
        preference_csv.append([category.name for category in preference.categories])
        preference_csv.append([format_obj.name for format_obj in preference.formats])
        preference_csv.append([author.name for author in preference.authors])
        preference_csv.append([serie.name for serie in preference.series])
        preference_csv.append(preference.child_id)

        master_csv.append(preference_csv)

    with open("export_data/preference.csv", 'a+') as f:
        writer = csv.writer(f)
        for row in master_csv:
            writer.writerow(row)
        f.close()