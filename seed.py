def seed():
    import csv

    from app import db

    from app.models.books import Book

    books = []

    with open("app/data/books.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            books.append(line)

    books = books[1:1001]

    from app.models.author import Author
    from app.models.illustrator import Illustrator

    authors = []
    illustrators = []

    with open("app/data/creators.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            if 'auth' in line[1].lower():
                authors.append(line)
            elif "illus" in line[1].lower():
                illustrators.append(line)

    from app.models.series import Series

    series = []

    with open("app/data/series.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            series.append(line)

    series = series[1:]

    from app.models.annotations import Annotation

    annotations = []

    with open("app/data/annotations.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            annotations.append(line)

    annotations = annotations[1:]

    from app.models.reviews import Review

    reviews = []

    with open("app/data/reviews.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            reviews.append(line)

    reviews = reviews[1:]

    from app.models.details import Detail

    details = []

    with open("app/data/product_details.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            details.append(line)

    details = details[2:]

    from app.models.category import Category

    categories = []

    with open("app/data/categories.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            categories.append(line)

    categories = categories[1:]

    annotation_dict = {}
    for annotation in annotations:
        if not annotation_dict.get(annotation[0]):
            annotation_dict[annotation[0]] ={}
        if "about" in annotation[1].lower():
            annotation_dict[annotation[0]]["about_title"] = annotation[1]
            annotation_dict[annotation[0]]["about_text"] = annotation[2]
        elif annotation[1].lower() == "review text":
            annotation_dict[annotation[0]]["review_text"] = annotation[2]
        elif annotation[1].lower() == "review quote":
            annotation_dict[annotation[0]]["review_quote"] = annotation[2]

    product_details = {}
    for detail in details:
        if not product_details.get(detail[8]):
            product_details[detail[8]] = {}
        product_details[detail[8]]["age_group1"] = True if detail[0].split(" ")[0] == "0-2" else False
        product_details[detail[8]]["age_group2"] = True if detail[0].split(" ")[0] == "3-5" else False
        product_details[detail[8]]["age_group3"] = True if detail[0].split(" ")[0] == "6-8" else False
        product_details[detail[8]]["age_group4"] = True if detail[0].split(" ")[0] == "9-11" else False
        product_details[detail[8]]["age_group5"] = True if detail[0][:2].lower == "ya" else False
        product_details[detail[8]]["age_group6"] = True if detail[0][:2].lower == "ya" else False
        product_details[detail[8]]["for_age"] = detail[1]
        product_details[detail[8]]["pages"] = detail[2]
        product_details[detail[8]]["language"] = detail[3]
        product_details[detail[8]]["dimensions"] = detail[4]
        product_details[detail[8]]["publisher"] = detail[5]
        product_details[detail[8]]["publication_date"] = detail[6]
        product_details[detail[8]]["bestseller_rank"] = detail[9]
        product_details[detail[8]]["publication_location"] = detail[10]
        product_details[detail[8]]["edition_statement"] = detail[11]
        product_details[detail[8]]["edition"] = detail[12]
        product_details[detail[8]]["imprint"] = detail[13]
        product_details[detail[8]]["illustration_notes"] = detail[14]


    for author in authors:
        try:
            Author.create(author[2])
        except:
            db.session.rollback()
            pass

    for illustrator in illustrators:
        try:
            Illustrator.create(illustrator[2])
        except:
            db.session.rollback()
            pass

    for series_item in series:
        Series.create(series_item[0])

    unique_categories = []
    for category in categories:
        unique_categories.append(category[1])
    unique_categories = list(set(unique_categories))
    for category in unique_categories:
        Category.create(category)

    print(f"Total Books - {len(books)}")
    counter = 0
    for book in books:
        isbn = book[0]
        series_id_csv = book[6]
        if int(series_id_csv) == -1:
            series_id = None
        else:
            for series_item in series:
                if series_id_csv == series_item[1]:
                    series_id = Series.query.filter_by(name=series_item[0]).first().id
                    break
        
        Book.create(
            book[2], #name
            book[1], #image
            book[0], #isbn
            book[3], #rating
            book[4], #review_count
            book[5], #book_format
            book[7], #language
            book[8], #price
            book[9], #description
            series_id
        )

        book_obj = Book.query.filter_by(isbn=isbn).first()

        for author in authors:
            if author[0] == isbn:
                author_obj = Author.query.filter_by(name=author[2]).first()
                author_obj.books.append(book_obj)
                db.session.add(author_obj)
                db.session.commit()
        
        for illustrator in illustrators:
            if illustrator[0] == isbn:
                illustrator_obj = Illustrator.query.filter_by(name=illustrator[2]).first()
                illustrator_obj.books.append(book_obj)
                db.session.add(illustrator_obj)
                db.session.commit()

        for category in categories:
            if category[0] == isbn:
                category_obj = Category.query.filter_by(name=category[1]).first()
                category_obj.books.append(book_obj)
                db.session.add(category_obj)
                db.session.commit()

        current_annotation_dict = annotation_dict.get(isbn)
        if current_annotation_dict:
            Annotation.create(
                current_annotation_dict.get("about_title"),
                current_annotation_dict.get("about_text"),
                current_annotation_dict.get("review_text"),
                current_annotation_dict.get("review_quote"),
                book_obj.id
            )
        
        product_details_dict = product_details.get(isbn)
        Detail.create(
            product_details_dict.get("age_group1"),
            product_details_dict.get("age_group2"),
            product_details_dict.get("age_group3"),
            product_details_dict.get("age_group4"),
            product_details_dict.get("age_group5"),
            product_details_dict.get("age_group6"),
            product_details_dict.get("for_age"),
            product_details_dict.get("pages"),
            product_details_dict.get("language"),
            product_details_dict.get("dimensions"),
            product_details_dict.get("publisher"),
            product_details_dict.get("publication_date"),
            product_details_dict.get("bestseller_rank"),
            product_details_dict.get("publication_location"),
            product_details_dict.get("edition_statement"),
            product_details_dict.get("edition"),
            product_details_dict.get("imprint"),
            product_details_dict.get("illustration_notes"),
            book_obj.id
        )

        for review in reviews:
            if review[0] == isbn:
                Review.create(
                    review[1], #review
                    review[2], #author
                    book_obj.id
                )
        
        counter += 1
        print(counter)