import csv

from app import db

from app.models.annotations import Annotation
from app.models.author import Author
from app.models.books import Book
from app.models.category import Category
from app.models.details import Detail
from app.models.publishers import Publisher
from app.models.reviews import Review
from app.models.series import Series

import time

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


def seed():
    start = time.process_time()
    print("Processing")

    ##################################### AMAZON
    amazon_dict = {}
    print("Processing Amazon")
    amazon_books = []
    with open("app/data/new/amazon.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            amazon_books.append(line)

    amazon_books = amazon_books[1:]

    for book in amazon_books:
        if amazon_dict.get(book[0]):
            #Duplicate
            current_dict = amazon_dict[book[0]]
            if book[1] not in current_dict.get("category"):
                current_dict.get("category").append(book[1])
        else:
            amazon_dict[book[0]] = {}
            current_dict = amazon_dict[book[0]]
            current_dict["category"] = ["Amazon Bestseller", book[1]]
            current_dict["reviews"] = book[2]
            current_dict["rating"] = book[3]
            current_dict["name"] = book[4]
            current_dict["author"] = book[5]
            current_dict["publishing_date"] = book[6]
            current_dict["quality"] = book[7]
            current_dict["price"] = book[8]
            current_dict["age_group"] = book[9]
            current_dict["book_link"] = book[10]

    ######################################## Books
    book_dict = {}

    print("Processing Books")

    books = []
    with open("app/data/new/books.csv", mode="r") as file:
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

        if amazon_dict.get(book[0]):
            current_dict["rating"] = amazon_dict.get(book[0]).get("rating")
            current_dict["reviews"] = amazon_dict.get(book[0]).get("reviews")
            current_dict["categories"] = amazon_dict.get(book[0]).get("category")
        else:
            current_dict["rating"] = book[3]
            current_dict["reviews"] = book[4]
            current_dict["categories"] = []

    ########################################## Annotations
    annotation_dict = {}

    print("Processing Annotations")

    annotations = []
    with open("app/data/new/annotations.csv", mode="r") as file:
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
    with open("app/data/new/creators.csv", mode="r") as file:
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
    with open("app/data/new/categories.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            categories.append(line)
    categories = categories[1:]
    for category in categories:
        if book_dict.get(category[0]):
            current_dict = book_dict.get(category[0]).get("categories")
            if category[1] not in current_dict:
                current_dict.append(category[1])

    most_borrowed = []
    with open("app/data/new/most_borrowed.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            most_borrowed.append(line[0])
    most_borrowed = most_borrowed[1:]
    for isbn in most_borrowed:
        if book_dict.get(isbn):
            current_dict = book_dict.get(isbn).get("categories")
            if "Most Borrowed" not in current_dict:
                current_dict.append("Most Borrowed")
    ######################################## Product Details
    detail_dict = {}
    print("Processing Product Details")

    details = []
    with open("app/data/new/product_details.csv", mode="r") as file:
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
    with open("app/data/new/reviews.csv", mode="r") as file:
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

    #### Seeding Authors
    print("Seeding Authors")

    author_data = {}
    for isbn, people in author_dict.items():
        age_category = detail_dict[isbn]["age_category"]
        for item in people["authors"]:
            if not author_data.get(item):
                author_data[item] = {
                    "author_type": "author",
                    "age1_books": 0,
                    "age2_books": 0,
                    "age3_books": 0,
                    "age4_books": 0,
                    "age5_books": 0,
                    "total_books": 0
                }
            author_data[item]["total_books"] += 1
            if age_category == 1:
                author_data[item]["age1_books"] += 1
            elif age_category == 2:
                author_data[item]["age2_books"] += 1
            elif age_category == 3:
                author_data[item]["age3_books"] += 1
            elif age_category == 4:
                author_data[item]["age4_books"] += 1
            elif age_category == 5:
                author_data[item]["age5_books"] += 1
        for item in people["illustrators"]:
            if not author_data.get(item):
                author_data[item] = {
                    "author_type": "illustrator",
                    "age1_books": 0,
                    "age2_books": 0,
                    "age3_books": 0,
                    "age4_books": 0,
                    "age5_books": 0,
                    "total_books": 0
                }
            author_data[item]["total_books"] += 1
            if age_category == 1:
                author_data[item]["age1_books"] += 1
            elif age_category == 2:
                author_data[item]["age2_books"] += 1
            elif age_category == 3:
                author_data[item]["age3_books"] += 1
            elif age_category == 4:
                author_data[item]["age4_books"] += 1
            elif age_category == 5:
                author_data[item]["age5_books"] += 1

    for name, data in author_data.items():
        Author.create(
            name,
            data["author_type"],
            data["age1_books"],
            data["age2_books"],
            data["age3_books"],
            data["age4_books"],
            data["age5_books"],
            data["total_books"]
        )

    Author.create(
        "Unknown",
        "author",
        0,
        0,
        0,
        0,
        0,
        0
    )

    #### Seeding Categories
    print("Seeding Categories")

    category_data = {}
    for isbn, data in book_dict.items():
        try:
            age_category = detail_dict[isbn]["age_category"]
            for item in data.get("categories"):
                if not category_data.get(item):
                    category_data[item] = {
                        "age1_books": 0,
                        "age2_books": 0,
                        "age3_books": 0,
                        "age4_books": 0,
                        "age5_books": 0,
                        "total_books": 0
                    }
                category_data[item]["total_books"] += 1
                if age_category == 1:
                    category_data[item]["age1_books"] += 1
                elif age_category == 2:
                    category_data[item]["age2_books"] += 1
                elif age_category == 3:
                    category_data[item]["age3_books"] += 1
                elif age_category == 4:
                    category_data[item]["age4_books"] += 1
                elif age_category == 5:
                    category_data[item]["age5_books"] += 1
        except:
            pass

    for name, data in category_data.items():
        Category.create(
            name,
            data["age1_books"],
            data["age2_books"],
            data["age3_books"],
            data["age4_books"],
            data["age5_books"],
            data["total_books"]
        )

    #### Seeding Publishers
    print("Seeding Publishers")

    publisher_data = {}
    for isbn, publisher in publisher_dict.items():
        age_category = detail_dict[isbn]["age_category"]
        for item in publisher:
            if not publisher_data.get(item):
                publisher_data[item] = {
                    "age1_books": 0,
                    "age2_books": 0,
                    "age3_books": 0,
                    "age4_books": 0,
                    "age5_books": 0,
                    "total_books": 0
                }
            publisher_data[item]["total_books"] += 1
            if age_category == 1:
                publisher_data[item]["age1_books"] += 1
            elif age_category == 2:
                publisher_data[item]["age2_books"] += 1
            elif age_category == 3:
                publisher_data[item]["age3_books"] += 1
            elif age_category == 4:
                publisher_data[item]["age4_books"] += 1
            elif age_category == 5:
                publisher_data[item]["age5_books"] += 1

    for name, data in publisher_data.items():
        Publisher.create(
            name,
            data["age1_books"],
            data["age2_books"],
            data["age3_books"],
            data["age4_books"],
            data["age5_books"],
            data["total_books"]
        )

    #### Seeding Series
    print("Seeding Series")

    series_dict = {}
    for serie in series:
        if not series_dict.get(serie[1]):
            series_dict[serie[1]] = {
                "name": serie[0],
                "isbn":  []
            }
        for book in books:
            if serie[1] == book[6]:
                series_dict[serie[1]]["isbn"].append(book[0])
    
    series_data = {}
    for series_id, data in series_dict.items():
        try:
            series_data[data["name"]]  = {
                "age1_books": 0,
                "age2_books": 0,
                "age3_books": 0,
                "age4_books": 0,
                "age5_books": 0,
                "total_books": 0
            }
            for isbn in data["isbn"]:
                age_category = detail_dict[isbn]["age_category"]
                series_data[data["name"]]["total_books"] += 1
                if age_category == 1:
                    series_data[data["name"]]["age1_books"] += 1
                elif age_category == 2:
                    series_data[data["name"]]["age2_books"] += 1
                elif age_category == 3:
                    series_data[data["name"]]["age3_books"] += 1
                elif age_category == 4:
                    series_data[data["name"]]["age4_books"] += 1
                elif age_category == 5:
                    series_data[data["name"]]["age5_books"] += 1
        except:
            pass

    for name, data in series_data.items():
        Series.create(
            name,
            data["age1_books"],
            data["age2_books"],
            data["age3_books"],
            data["age4_books"],
            data["age5_books"],
            data["total_books"]
        )

    #### Seeding Books
    print("Seeding Books")

    for book_isbn, book_data in book_dict.items():
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
            series_id
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
            Review.create(
                review["review"],
                review["author"],
                book_obj.id
            )

    print(time.process_time() - start)