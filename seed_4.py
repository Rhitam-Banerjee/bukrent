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
from app.models.format import Format
from app.models.user import User, Address

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

def seed():
    print("Processing")

    ############################# Books
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
        current_dict["rating"] = book[3]
        current_dict["reviews"] = book[4]
        current_dict["categories"] = []
        current_dict["bestseller_json"] = None
        current_dict["borrowed_json"] = None
        current_dict["suggestion_json"] = None

    ################################# Bestseller
    print("Processing Bestsellers")

    bestsellers = []
    with open("app/data/data_3/bestseller.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            bestsellers.append(line)

    bestsellers = bestsellers[1:]

    for bestseller in bestsellers:
        current_dict = book_dict.get(bestseller[0])
        if current_dict:
            bestseller_groups = get_age_groups(bestseller[2])
            current_dict["bestseller_json"] = {
                "amazon_bestseller": True,
                "bestseller_age1": bestseller_groups[0],
                "bestseller_age2": bestseller_groups[1],
                "bestseller_age3": bestseller_groups[2],
                "bestseller_age4": bestseller_groups[3],
                "bestseller_age5": bestseller_groups[4],
                "bestseller_age6": bestseller_groups[5]
            }

    ###################################### Most Borrowed
    print("Processing Most Borrowed")
    
    most_borrowed = []
    with open("app/data/data_3/borrowed.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            most_borrowed.append(line)

    most_borrowed = most_borrowed[1:]

    for borrowed in most_borrowed:
        current_dict = book_dict.get(borrowed[0])
        if current_dict:
            borrowed_groups = get_age_groups(borrowed[1])
            current_dict["borrowed_json"] = {
                "most_borrowed": True,
                "borrowed_age1": borrowed_groups[0],
                "borrowed_age2": borrowed_groups[1],
                "borrowed_age3": borrowed_groups[2],
                "borrowed_age4": borrowed_groups[3],
                "borrowed_age5": borrowed_groups[4],
                "borrowed_age6": borrowed_groups[5]
            }

    ###################################### Suggestions
    print("Processing Suggestions")
    
    suggestions = []
    with open("app/data/data_3/suggestions.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            suggestions.append(line)

    suggestions = suggestions[1:]

    suggestion_dict = {}
    for suggestion in suggestions:
        for index, isbn in enumerate(suggestion):
            if index == 0:
                age_group = "0-2"
            elif index == 1:
                age_group = "3-5"
            elif index == 2:
                age_group = "6-8"
            elif index == 3:
                age_group = "6-8"
            elif index == 4:
                age_group = "9-11"
            elif index == 5:
                age_group = "12-14"
            elif index == 6:
                age_group = "15+"
            if isbn:
                if suggestion_dict.get(isbn):
                    suggestion_dict[isbn].append(age_group)
                else:
                    suggestion_dict[isbn] = [age_group]

    for isbn, age_groups in suggestion_dict.items():
        current_dict = book_dict.get(isbn)
        if current_dict:
            suggestion_groups = get_multi_age_groups(age_groups)
            current_dict["suggestion_json"] = {
                "suggestion_age1": suggestion_groups[0],
                "suggestion_age2": suggestion_groups[1],
                "suggestion_age3": suggestion_groups[2],
                "suggestion_age4": suggestion_groups[3],
                "suggestion_age5": suggestion_groups[4],
                "suggestion_age6": suggestion_groups[5]
            }

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

    Author.create(
        "Unknown",
        "author",
        False,
        False,
        False,
        False,
        False,
        False,
        0,
        False
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

    ########################### Seeding Preference Categories
    preference = []
    with open("app/data/preferences.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            preference.append(line)

    pref_dict = {}
    for pref in preference:
        if pref_dict.get(pref[0]):
            if pref[1] not in pref_dict[pref[0]]:
                pref_dict[pref[0]].append(pref[1])
        else:
            pref_dict[pref[0]] = [pref[1]]

    for name, age_groups in pref_dict.items():
        category = Category.query.filter_by(name=name).first()
        ages = get_multi_age_groups(age_groups)
        if category:
            category.age1 = ages[0]
            category.age2 = ages[1]
            category.age3 = ages[2]
            category.age4 = ages[3]
            category.age5 = ages[4]
            category.age6 = ages[5]
            category.display = True

            db.session.add(category)
            db.session.commit()
        else:
            Category.create(
                name,
                ages[0],
                ages[1],
                ages[2],
                ages[3],
                ages[4],
                ages[5],
                0,
                True
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

    ########################################## Seeding Formats
    format_dict = {}

    print("Processing Formats")

    formats = []
    with open("app/data/formats.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            formats.append(line)

    for format_name in formats:
        Format.create(
            format_name[0],
            True,
            True,
            True,
            True,
            True,
            True,
            0,
            True
        )