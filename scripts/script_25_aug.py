from app.models.user import *
from app.models.buckets import *
from app.models.order import *
from app.models.books import Book

from app.models.annotations import Annotation
from app.models.author import Author
from app.models.category import Category
from app.models.details import Detail
from app.models.publishers import Publisher
from app.models.reviews import Review
from app.models.series import Series
from app.models.format import Format

from app import db

import datetime
import csv

def get_multi_age_groups(ages):
    age_groups = []
    for age in ages:
        age_groups.append(get_age_groups(age))
    final_age_group = [False, False, False, False, False, False]
    for age_group in age_groups:
        if age_group[0]:
            final_age_group[0] = True
        if age_group[1]:
            final_age_group[1] = True
        if age_group[2]:
            final_age_group[2] = True
        if age_group[3]:
            final_age_group[3] = True
        if age_group[4]:
            final_age_group[4] = True
        if age_group[5]:
            final_age_group[5] = True
    return final_age_group

def get_age_categories(detail):
    if detail[0].replace(" ", "") in ["0-5", "0-2", "1+"]:
        return 1
    elif detail[0].replace(" ", "") in ["3-5", "3+", "2-6"]:
        return 2
    elif detail[0].replace(" ", "") in ["5+", "6-8", "6-12", "6+", "7+"]:
        return 3
    elif detail[0].replace(" ", "") in ["9+", "9-12", "6-12", "8+", "10+"]:
        return 4
    elif detail[0].replace(" ", "") in ["12-17", "14+", "13+", "12+", "11+", "15+", "16+"]:
        return 5

def get_age_groups(age_group):
    if age_group == "6-8":
        return [False, False, True, False, False, False]
    elif age_group == "9-11":
        return [False, False, False, True, False, False]
    elif age_group == "0-5":
        return [True, True, False, False, False, False]
    elif age_group == "12+":
        return [False, False, False, False, True, True]
    elif age_group == "0+":
        return [True, True, True, True, True, True]
    elif age_group == "3-5":
        return [False, True, False, False, False, False]
    elif age_group == "12-14":
        return [False, False, False, False, True, False]
    elif age_group == "0-2":
        return [True, False, False, False, False, False]
    elif age_group == "15+":
        return [False, False, False, False, False, True]
    return [False, False, False, False, False, False]

def add_books():
    print("Processing")

    ############################# Books
    book_dict = {}

    print("Processing Books")

    books = []
    with open("scripts/data/25_aug/books/books.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            books.append(line)

    books = books[1:]

    for book in books:
        book_dict[book[0]] = {}
        current_dict = book_dict[book[0]]
        current_dict["name"] = book[2]
        current_dict["image"] = book[1]
        current_dict["format"] = book[5]
        current_dict["series_id"] = book[6]
        current_dict["language"] = book[7]
        current_dict["price"] = book[8]
        current_dict["description"] = book[9]
        current_dict["rating"] = book[3]
        current_dict["reviews"] = book[4]
        current_dict["categories"] = []
        current_dict["bestseller_json"] = None
        current_dict["borrowed_json"] = None
        current_dict["suggestion_json"] = None

    ########################################## Annotations
    annotation_dict = {}

    print("Processing Annotations")

    annotations = []
    with open("scripts/data/25_aug/books/annotations.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            annotations.append(line)

    annotations = annotations[1:]

    for annotation in annotations:
        if annotation_dict.get(annotation[0]):
            current_dict = annotation_dict[annotation[0]]
            if "table" in annotation[1].lower():
                current_dict["table_of_contents"] = annotation[1]
            elif "text" in annotation[1].lower():
                current_dict["review_text"] = annotation[1]
            elif "quote" in annotation[1].lower():
                current_dict["review_quote"] = annotation[1]
            elif "flap" in annotation[1].lower():
                current_dict["flap_copy"] = annotation[1]
            elif "back" in annotation[1].lower():
                current_dict["back_cover_copy"] = annotation[1]
            elif "about" in annotation[1].lower():
                current_dict["about_author"] = annotation[1]
        else:
            if book_dict.get(annotation[0]):
                annotation_dict[annotation[0]] = {}
                current_dict = annotation_dict[annotation[0]]
                if "table" in annotation[1].lower():
                    current_dict["table_of_contents"] = annotation[1]
                elif "text" in annotation[1].lower():
                    current_dict["review_text"] = annotation[1]
                elif "quote" in annotation[1].lower():
                    current_dict["review_quote"] = annotation[1]
                elif "back" in annotation[1].lower():
                    current_dict["back_cover_copy"] = annotation[1]
                elif "about" in annotation[1].lower():
                    current_dict["about_author"] = annotation[1]

    #################################### Authors
    author_dict = {}
    print("Processing Authors")
    authors = []
    with open("scripts/data/25_aug/books/creators.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            authors.append(line)

    authors = authors[1:]

    for author in authors:
        if author_dict.get(author[0]):
            current_dict = author_dict[author[0]]
            if "author" in author[1].lower():
                current_dict["authors"].append(author[2])
            else:
                current_dict["illustrators"].append(author[2])
        else:
            if book_dict.get(author[0]):
                author_dict[author[0]] = {
                    "authors": [],
                    "illustrators": []
                }
                current_dict = author_dict[author[0]]
                if "author" in author[1].lower():
                    current_dict["authors"].append(author[2])
                else:
                    current_dict["illustrators"].append(author[2])

    ##################################### Categories
    categories = []
    with open("scripts/data/25_aug/books/categories.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            categories.append(line)
    categories = categories[1:]
    for category in categories:
        if book_dict.get(category[0]):
            current_dict = book_dict.get(category[0]).get("categories")
            if category[1] not in current_dict:
                current_dict.append(category[1])

    ######################################## Product Details
    detail_dict = {}
    print("Processing Product Details")

    details = []
    with open("scripts/data/25_aug/books/product_details.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            details.append(line)

    details = details[1:]

    for detail in details:
        if detail_dict.get(detail[7]):
            current_dict = detail_dict[detail[7]]
            current_dict["age_category"] = get_age_categories(detail)
            current_dict["for_age"] = detail[0]
            current_dict["pages"] = detail[1]
            current_dict["language"] = detail[2]
            current_dict["dimensions"] = detail[3]
            current_dict["publisher"] = detail[4]
            current_dict["publication_date"] = detail[5]
            current_dict["bestseller_rank"] = detail[8]
            current_dict["publication_location"] = detail[9]
            current_dict["edition_statement"] = detail[10]
            current_dict["edition"] = detail[11]
            current_dict["imprint"] = detail[12]
            current_dict["illustration_notes"] = detail[13]
        else:
            if book_dict.get(detail[7]):
                detail_dict[detail[7]] = {}
                current_dict = detail_dict[detail[7]]
                current_dict["age_category"] = get_age_categories(detail)
                current_dict["for_age"] = detail[0]
                current_dict["pages"] = detail[1]
                current_dict["language"] = detail[2]
                current_dict["dimensions"] = detail[3]
                current_dict["publisher"] = detail[4]
                current_dict["publication_date"] = detail[5]
                current_dict["bestseller_rank"] = detail[8]
                current_dict["publication_location"] = detail[9]
                current_dict["edition_statement"] = detail[10]
                current_dict["edition"] = detail[11]
                current_dict["imprint"] = detail[12]
                current_dict["illustration_notes"] = detail[13]

    ################################### Publishers
    publisher_dict = {}
    print("Processing Publishers")

    for detail in details:
        if publisher_dict.get(detail[7]):
            publisher_dict[detail[7]].append(detail[4])
        else:
            if book_dict.get(detail[7]):
                publisher_dict[detail[7]] = []
                publisher_dict[detail[7]].append(detail[4])

    ######################################### Reviews
    review_dict = {}
    print("Processing Reviews")

    reviews = []
    with open("scripts/data/25_aug/books/reviews.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            reviews.append(line)

    reviews = reviews[1:]

    for review in reviews:
        if review_dict.get(review[0]):
            current_dict = review_dict[review[0]]
            current_dict.append({
                "review": review[1],
                "author": review[2]
            })
        else:
            if book_dict.get(review[0]):
                review_dict[review[0]] = []
                current_dict = review_dict[review[0]]
                current_dict.append({
                    "review": review[1],
                    "author": review[2]
                })

    ################################## Series
    print("Processing Series")

    series = []
    with open("app/data/series.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            series.append(line)

    series = series[1:]

    ################################################# Seeding Authors
    authors_age = []

    with open("app/data/data_3/authors.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            authors_age.append(line)

    authors_age = authors_age[1:]

    author_age_dict = {}
    for author_age in authors_age:
        if author_age_dict.get(author_age[0]):
            author_age_dict[author_age[0]].append(author_age[2])
        else:
            author_age_dict[author_age[0]] = [author_age[2]]

    print("Seeding Authors")

    author_data = {}

    for isbn, people in author_dict.items():
        for item in people["authors"]:
            ages = [False, False, False, False, False, False]
            display = False
            if not author_data.get(item):
                if author_age_dict.get(item):
                    ages = get_multi_age_groups(author_age_dict.get(item))
                    display = True
                author_data[item] = {
                    "author_type": "author",
                    "age1": ages[0],
                    "age2": ages[1],
                    "age3": ages[2],
                    "age4": ages[3],
                    "age5": ages[4],
                    "age6": ages[5],
                    "total_books": 0,
                    "display": display
                }
            author_data[item]["total_books"] += 1
        for item in people["illustrators"]:
            ages = [False, False, False, False, False, False]
            display = False
            if not author_data.get(item):
                if author_age_dict.get(item):
                    for age in author_age_dict.get(item):
                        ages = get_age_groups(age)
                        display = True
                author_data[item] = {
                    "author_type": "illustrator",
                    "age1": ages[0],
                    "age2": ages[1],
                    "age3": ages[2],
                    "age4": ages[3],
                    "age5": ages[4],
                    "age6": ages[5],
                    "total_books": 0,
                    "display": display
                }
            author_data[item]["total_books"] += 1

    for name, data in author_data.items():
        author_obj = Author.query.filter_by(name=name).first()
        if not author_obj:
            Author.create(
                name,
                data["author_type"],
                data["age1"],
                data["age2"],
                data["age3"],
                data["age4"],
                data["age5"],
                data["age6"],
                data["total_books"],
                data["display"]
            )

    #### Seeding Categories
    print("Seeding Categories")

    category_data = {}
    for isbn, data in book_dict.items():
        try:
            for item in data.get("categories"):
                if not category_data.get(item):
                    category_data[item] = {
                        "age1": False,
                        "age2": False,
                        "age3": False,
                        "age4": False,
                        "age5": False,
                        "age6": False,
                        "total_books": 0,
                        "display": False
                    }
                category_data[item]["total_books"] += 1
        except:
            pass

    for name, data in category_data.items():
        category_obj = Category.query.filter_by(name=name).first()
        if not category_obj:
            Category.create(
                name,
                data["age1"],
                data["age2"],
                data["age3"],
                data["age4"],
                data["age5"],
                data["age6"],
                data["total_books"],
                data["display"]
            )

    #### Seeding Publishers
    print("Seeding Publishers")

    publisher_data = {}
    for isbn, publisher in publisher_dict.items():
        for item in publisher:
            if not publisher_data.get(item):
                publisher_data[item] = {
                    "age1": True,
                    "age2": True,
                    "age3": True,
                    "age4": True,
                    "age5": True,
                    "age6": True,
                    "total_books": 0,
                    "display": True
                }
            publisher_data[item]["total_books"] += 1

    for name, data in publisher_data.items():
        publisher_obj = Publisher.query.filter_by(name=name).first()
        if not publisher_obj:
            Publisher.create(
                name,
                data["age1"],
                data["age2"],
                data["age3"],
                data["age4"],
                data["age5"],
                data["age6"],
                data["total_books"],
                data["display"]
            )

    #### Seeding Series
    print("Seeding Series")

    series_dict = {}
    for serie in series:
        if not series_dict.get(serie[1]):
            series_dict[serie[1]] = {
                "name": serie[0],
                "id": serie[1],
                "isbn":  []
            }
        for book in books:
            if serie[1] == book[6]:
                series_dict[serie[1]]["isbn"].append(book[0])

    series_age = []

    with open("app/data/data_3/series.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            series_age.append(line)

    series_age = series_age[1:]

    series_age_dict = {}
    for serie_age in series_age:
        if series_age_dict.get(serie_age[1]):
            series_age_dict[serie_age[1]].append(serie_age[0])
        else:
            series_age_dict[serie_age[1]] = [serie_age[0]]
    
    series_data = {}
    for series_id, data in series_dict.items():
        try:
            series_data[data["name"]]  = {
                "id": data["id"],
                "total_books": 0
            }
            for isbn in data["isbn"]:
                series_data[data["name"]]["total_books"] += 1
        except:
            pass

    for name, data in series_data.items():
        ages = series_age_dict.get(data["id"])
        if ages:
            age_groups = get_multi_age_groups(ages)
            display = True
        else:
            age_groups = [False, False, False, False, False, False]
            display = False
        
        series_obj = Series.query.filter_by(name=name).first()
        if not series_obj:
            Series.create(
                name,
                age_groups[0],
                age_groups[1],
                age_groups[2],
                age_groups[3],
                age_groups[4],
                age_groups[5],
                data["total_books"],
                display
            )
    
    #### Seeding Books
    print("Seeding Books")

    for book_isbn, book_data in book_dict.items():
        existing_book_obj = Book.query.filter_by(isbn=book_isbn).first()

        if not existing_book_obj:
            if not detail_dict.get(book_isbn):
                print(book_isbn)
                continue
            series = book_data["series_id"]
            series_name = series_dict.get(series)
            series_id = None
            if series_name:
                series_name = series_name["name"]
                series_id = Series.query.filter_by(name=series_name).first().id

            Book.create(
                book_data["name"],
                book_data["image"],
                book_isbn,
                book_data["rating"],
                book_data["reviews"],
                book_data["format"],
                book_data["language"],
                book_data["price"],
                book_data["description"],
                1,
                series_id,
                book_data["bestseller_json"],
                book_data["borrowed_json"],
                book_data["suggestion_json"]
            )

            book_obj = Book.query.filter_by(isbn=book_isbn).first()

            categories = book_data.get("categories")
            if categories:
                for item in categories:
                    obj = Category.query.filter_by(name=item).first()
                    obj.books.append(book_obj)
                    db.session.add(obj)
                    db.session.commit()

            publishers = publisher_dict.get(book_isbn)
            if publishers:
                for item in publishers:
                    obj = Publisher.query.filter_by(name=item).first()
                    obj.books.append(book_obj)
                    db.session.add(obj)
                    db.session.commit()
            
            authors = author_dict.get(book_isbn)
            if authors:
                total_authors = len(authors["authors"]) + len(authors["illustrators"])
                if total_authors == 0:
                    obj = Author.query.filter_by(name="Unknown").first()
                    obj.books.append(book_obj)
                    db.session.add(obj)
                    db.session.commit()
                else:
                    for item in authors["authors"]:
                        obj = Author.query.filter_by(name=item).first()
                        obj.books.append(book_obj)
                        db.session.add(obj)
                        db.session.commit()
                    for item in authors["illustrators"]:
                        obj = Author.query.filter_by(name=item).first()
                        obj.books.append(book_obj)
                        db.session.add(obj)
                        db.session.commit()
            else:
                obj = Author.query.filter_by(name="Unknown").first()
                obj.books.append(book_obj)
                db.session.add(obj)
                db.session.commit()

    #### Seeding Annotations
    print("Seeding Annotations")

    for isbn, data in annotation_dict.items():
        book_obj = Book.query.filter_by(isbn=isbn).first()
        if not book_obj.annotation:
            Annotation.create(
                data.get("table_of_contents"),
                data.get("review_text"),
                data.get("review_quote"),
                data.get("flap_copy"),
                data.get("back_cover_copy"),
                data.get("about_author"),
                book_obj.id
            )

    #### Seeding Details
    print("Seeding Product Details")

    for isbn, data in detail_dict.items():
        book_obj = Book.query.filter_by(isbn=isbn).first()
        try:
            bestseller_rank = int(data.get("bestseller_rank"))
        except:
            bestseller_rank = 10000000
        if not book_obj.details:
            Detail.create(
                data.get("age_category"),
                data.get("for_age"),
                data.get("pages"),
                data.get("language"),
                data.get("dimensions"),
                data.get("publisher"),
                data.get("publication_date"),
                bestseller_rank,
                data.get("publication_location"),
                data.get("edition_statement"),
                data.get("edition"),
                data.get("imprint"),
                data.get("illustration_notes"),
                book_obj.id
            )

    #### Seeding Reviews
    print("Seeding Reviews")

    for isbn, data in review_dict.items():
        book_obj = Book.query.filter_by(isbn=isbn).first()
        for review in data:
            review_obj = Review.query.filter_by(review=review["review"]).first()
            if not review_obj:
                Review.create(
                    review["review"],
                    review["author"],
                    book_obj.id
                )
            else:
                if review_obj.book_id != book_obj.id:
                    Review.create(
                        review["review"],
                        review["author"],
                        book_obj.id
                    )

def aug_25():
    buckets = DeliveryBucket.query.all()
    for bucket in buckets:
        bucket.delete()

    wishlists = Wishlist.query.all()
    for wishlist in wishlists:
        wishlist.delete()

    suggestions = Suggestion.query.all()
    for suggestion in suggestions:
        suggestion.delete()

    dumps = Dump.query.all()
    for dump in dumps:
        dump.delete()

    orders = Order.query.all()
    for order in orders:
        order.delete()

    books = Book.query.all()
    for book in books:
        book.stock_available = 1
        db.session.add(book)
        db.session.commit()

    users_data = []
    with open("scripts/data/25_aug/users.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            users_data.append(line)

    users_data = users_data[1:]

    for user_data in users_data:
        first_name = user_data[0].split(" ")[0]
        try:
            last_name = user_data[0].split(" ")[1]
        except:
            last_name = ""
        
        mobile_number = user_data[1]
        plan_id = user_data[2]

        password = user_data[3]
        day = user_data[4]

        if day == "sat":
            last_day = datetime.datetime.strptime("20-08-2022", "%d-%m-%Y")
            next_day = datetime.datetime.strptime("27-08-2022", "%d-%m-%Y")
        if day == "wed":
            last_day = datetime.datetime.strptime("24-08-2022", "%d-%m-%Y")
            next_day = datetime.datetime.strptime("31-08-2022", "%d-%m-%Y")

        user_obj = User.query.filter_by(mobile_number=mobile_number).first()
        if not user_obj:
            user_obj = User.create(first_name, last_name, mobile_number)

        if not user_obj.password:
            user_obj.password = password
        
        user_obj.is_subscribed = True
        user_obj.security_deposit = True
        user_obj.plan_id = plan_id
        user_obj.next_delivery_date = next_day
        user_obj.last_delivery_date = last_day
        user_obj.next_order_confirmed = False
        db.session.add(user_obj)
        db.session.commit()

    suggestions_data = []
    with open("scripts/data/25_aug/isbn.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            suggestions_data.append(line)

    suggestions_data = suggestions_data[1:]

    user_suggestion_dict = {}
    for mobile_number in suggestions_data[0]:
        user_suggestion_dict[mobile_number] = []

    for mobile_number, empty_list in user_suggestion_dict.items():
        user_obj = User.query.filter_by(mobile_number=mobile_number).first()
        column = suggestions_data[0].index(mobile_number)
        row = 0
        while row < int(suggestions_data[1][column]):
            if suggestions_data[row+2][column]:
                empty_list.append(suggestions_data[row+2][column])
                row += 1
    
    total_suggestions = 0
    for mobile_number, isbn_list in user_suggestion_dict.items():
        user_obj = User.query.filter_by(mobile_number=mobile_number).first()
        for isbn in isbn_list:
            book = Book.query.filter_by(isbn=isbn).first()
            if not book:
                isbn_list.remove(isbn)
            else:
                age_group = None
                if book.suggestion_age1:
                    age_group = 1
                elif book.suggestion_age2:
                    age_group = 2
                elif book.suggestion_age3:
                    age_group = 3
                elif book.suggestion_age4:
                    age_group = 4
                elif book.suggestion_age5:
                    age_group = 5
                elif book.suggestion_age6:
                    age_group = 6
                if not age_group:
                    if book.bestseller_age1:
                        age_group = 1
                    elif book.bestseller_age2:
                        age_group = 2
                    elif book.bestseller_age3:
                        age_group = 3
                    elif book.bestseller_age4:
                        age_group = 4
                    elif book.bestseller_age5:
                        age_group = 5
                    elif book.bestseller_age6:
                        age_group = 6
                    if not age_group:
                        book.suggestion_age3 = True
                        db.session.add(book)
                        db.session.commit()

                        age_group = 3

                Suggestion.create(user_obj.id, book.id, age_group)
        print(f"{mobile_number} has {len(isbn_list)} books")
        total_suggestions += len(isbn_list)

    print(f"Total suggestions - {total_suggestions}")
    print(f"Suggestions Created - {len(Suggestion.query.all())}")

def populate_suggestions():
    suggestions_data = []
    with open("scripts/data/25_aug/shreya.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            suggestions_data.append(line)

    for suggestion_isbn in suggestions_data:
        user_obj = User.query.filter_by(mobile_number='8826144375').first()
        book = Book.query.filter_by(isbn=suggestion_isbn).first()
        if not book:
            continue
        else:
            Suggestion.create(user_obj.id, book.id, 1)