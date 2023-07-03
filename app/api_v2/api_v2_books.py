from datetime import date, timedelta
from flask import jsonify, request
import random
import json

from sqlalchemy import Date, Integer, and_, cast, desc, or_

from app import db
from app.models.new_books import NewBookImage, NewBookSection, NewBook, NewCategory, NewCategoryBook
from app.models.order import Order
from app.models.buckets import Wishlist, Dump
from app.models.books import Book

from app.api_admin.utils import upload_to_aws
from app.api_v2.utils import api_v2_books

import os
import csv
import requests
import io


@api_v2_books.route('/get-book-set')
def get_book_set():
    age = request.args.get('age')

    section_name = request.args.get('section_name')
    start = request.args.get('start')
    end = request.args.get('end')
    if not section_name or age is None:
        return jsonify({"success": False, "message": "Provide age group and section name"})
    if not str(age).isnumeric():
        return jsonify({"success": False, "message": "Invalid age group"})
    if start and str(start).isnumeric():
        start = int(start)
    else:
        start = None
    if end and str(end).isnumeric():
        end = int(end)
    else:
        end = None
    section = NewBookSection.query.filter_by(name=section_name).first()
    if not section:
        return jsonify({"success": False, "message": "Invalid section name"})
    age = int(age)
    categories_query = NewCategory.query.filter(
        NewCategory.min_age <= age,
        NewCategory.max_age >= age
    ).order_by(NewCategory.category_order)
    if start is not None and end is not None:
        categories_query = categories_query.limit(end - start).offset(start)
    categories = categories_query.all()
    book_set = []
    if len(categories) > 1:
        shuffled_categories = categories[1:]
        random.shuffle(shuffled_categories)
        categories = [categories[0], *shuffled_categories]
    for category in categories:
        books = db.session.query(NewBook, NewCategoryBook).filter(
            NewBook.id == NewCategoryBook.book_id,
            NewCategoryBook.category_id == category.id,
            NewCategoryBook.section_id == section.id,
            NewBook.min_age <= age,
            NewBook.max_age >= age
        ).all()
        books = [book[0].to_json() for book in books]
        if category.name == 'Best Seller - Most Popular':
            random.shuffle(books)
        else:
            books = sorted(books, key=lambda book: int(
                book['review_count']), reverse=True)
        if len(books):
            book_set.append({
                "category": category.name,
                "books": books
            })
    return jsonify({"success": True, "book_set": book_set})


@api_v2_books.route('/get-most-popular-set')
def get_most_popular_set():
    age = request.args.get('age')
    count = request.args.get('count')
    category_limit = request.args.get('category_limit')
    if not str(age).isnumeric():
        return jsonify({"success": False, "message": "Invalid age group"})
    if not count or not count.isnumeric() or int(count) <= 0:
        return jsonify({"success": False, "message": "Invalid count"})
    if not category_limit or not category_limit.isnumeric() or int(category_limit) <= 0:
        return jsonify({"success": False, "message": "Invalid category limit"})
    age = int(age)
    count = int(count)
    category_limit = int(category_limit)
    categories = NewCategory.query.filter(
        NewCategory.min_age <= age,
        NewCategory.max_age >= age
    ).all()
    books = []
    book_ids = set()
    for category in categories:
        category_books = db.session.query(NewBook).join(NewCategoryBook, NewCategory).filter(
            NewBook.id == NewCategoryBook.book_id,
            NewCategoryBook.category_id == category.id,
            NewBook.min_age <= age,
            NewBook.max_age >= age,
        ).join(Book, NewBook.isbn == Book.isbn).filter(
            Book.stock_available > 0,
        ).order_by(desc(cast(NewBook.review_count, Integer))).limit(category_limit).all()
        for book in category_books:
            if book.id not in book_ids:
                books.append(book)
                book_ids.add(book.id)
    books = sorted(books, key=lambda book: int(
        book.review_count), reverse=True)[:count]
    books = [book.to_json() for book in books]
    return jsonify({"success": True, "books": books})


@api_v2_books.route('/get-must-read-set')
def get_must_read_set():
    age = request.args.get('age')
    category_count = request.args.get('category_count')
    book_count = request.args.get('book_count')
    section_name = request.args.get('section_name')
    show_unavailable = request.args.get('show_unavailable')
    randomize_categories = request.args.get('randomize_categories')
    randomize_books = request.args.get('randomize_books')
    if not str(age).isnumeric():
        return jsonify({"success": False, "message": "Invalid age group"}), 400
    if not category_count or not book_count:
        return jsonify({"success": False, "message": "Provide category and book count"}), 400
    if not category_count.isnumeric() or int(category_count) <= 0:
        return jsonify({"success": False, "message": "Invalid category count"}), 400
    if not book_count.isnumeric() or int(book_count) <= 0:
        return jsonify({"success": False, "message": "Invalid book count"}), 400
    section = NewBookSection.query.filter_by(name=section_name).first()
    if not section:
        return jsonify({"success": False, "message": "Invalid section name"}), 400
    age = int(age)
    category_count = int(category_count)
    book_count = int(book_count)
    categories = NewCategory.query.join(NewCategoryBook).filter(
        NewCategoryBook.section_id == section.id).all()
    book_set = []
    if len(categories) == 1 and categories[0].name == section.name:
        books_query = NewBook.query.join(NewCategoryBook).filter(
            NewBook.id == NewCategoryBook.book_id,
            NewCategoryBook.section_id == section.id,
            NewCategoryBook.category_id == categories[0].id,
            NewBook.min_age <= age,
            NewBook.max_age >= age
        )
        if not show_unavailable:
            books_query = books_query.join(
                Book, NewBook.isbn == Book.isbn).filter(Book.stock_available >= 1)
        books = books_query.order_by(
            desc(cast(NewBook.review_count, Integer))).all()
        category_to_books = dict()
        for book in books:
            categories = NewCategory.query.join(NewCategoryBook).filter(
                NewCategoryBook.section_id == 1,
                NewCategoryBook.book_id == book.id,
                NewCategory.max_age != 100,
            ).all()
            for category in categories:
                if category.name not in category_to_books:
                    category_to_books[category.name] = {
                        "category": category.name, "books": []}
                if len(category_to_books[category.name]["books"]) < book_count:
                    category_to_books[category.name]["books"].append(book)
        for category in category_to_books:
            if randomize_books:
                random.shuffle(category_to_books[category]["books"])
            book_set.append(category_to_books[category])
    else:
        for category in categories:
            books_query = NewBook.query.join(NewCategoryBook, NewCategory).filter(
                NewBook.id == NewCategoryBook.book_id,
                NewCategoryBook.category_id == category.id,
                NewBook.min_age <= age,
                NewBook.max_age >= age
            )
            if not show_unavailable:
                books_query = books_query.join(
                    Book, NewBook.isbn == Book.isbn).filter(Book.stock_available >= 1)
            books_all = books_query.order_by(
                desc(cast(NewBook.review_count, Integer))).all()
            books = []
            category_ids = set()
            for book in books_all:
                book_categories = NewCategoryBook.query.filter_by(
                    book_id=book.id, section_id=1).all()
                category_exists = False
                for book_category in book_categories:
                    if book_category.category_id in category_ids:
                        category_exists = True
                        break
                    category_ids.add(book_category.category_id)
                if not category_exists:
                    books.append(book)
                if len(books) == book_count:
                    break
            if randomize_books:
                random.shuffle(books)
            book_set.append({"category": category.name, "books": books})
    book_set = sorted(book_set, key=lambda category: sum(
        [int(book.review_count) for book in category["books"]]), reverse=True)[:category_count]
    if randomize_categories:
        random.shuffle(book_set)
    for i in range(category_count):
        book_set[i]["books"] = [book.to_json()
                                for book in book_set[i]["books"]]
    return jsonify({"success": True, "book_set": book_set})


@api_v2_books.route('/get-category-books')
def get_category_books():
    category_name = request.args.get('category_name')
    if not category_name:
        return jsonify({"success": False, "message": "Provide category name"}), 400
    category = NewCategory.query.filter_by(name=category_name).first()
    if not category:
        return jsonify({"success": False, "message": "Invalid category name"}), 400
    books = category.books
    random.shuffle(books)
    return jsonify({"success": True, "books": [book.to_json() for book in books]})


@api_v2_books.route('/get-new-books')
def get_new_books():
    start = request.args.get('start')
    end = request.args.get('end')
    age = request.args.get('age')
    category_id = request.args.get('category_id')
    search_query = request.args.get('search_query')
    section_id = request.args.get('section_id')
    sort_review_count = request.args.get('sort_review_count')
    if age and not str(age).isnumeric() and age != '-1':
        return jsonify({"success": False, "message": "Provide age group"}), 400
    if category_id and not NewCategory.query.filter_by(id=category_id).count():
        return jsonify({"success": False, "message": "Invalid category ID"}), 400
    if section_id and not NewBookSection.query.filter_by(id=section_id).count():
        return jsonify({"success": False, "message": "Invalid section ID"}), 400
    if not search_query:
        search_query = ''
    if not start or not start.isnumeric():
        start = 0
    if not end or not end.isnumeric():
        end = 10
    if str(age) == '-1':
        age = None
    elif age:
        age = int(age)
    start, end = int(start), int(end)
    books_query = db.session.query(NewBook)
    if search_query:
        books_query = books_query.join(NewCategoryBook, NewCategory).filter(
            or_(
                NewBook.name.ilike(f'{search_query}%'),
                NewBook.isbn.ilike(f'{search_query}%'),
                NewCategory.name.ilike(f'{search_query}%'),
            )
        )
    if age is not None:
        books_query = books_query.filter(
            NewBook.min_age <= age,
            NewBook.max_age >= age
        )
    if category_id and section_id:
        books_query = books_query.filter(
            NewBook.id == NewCategoryBook.book_id,
            NewCategoryBook.category_id == category_id,
            NewCategoryBook.section_id == section_id,
        )
    elif category_id:
        books_query = books_query.filter(
            NewBook.id == NewCategoryBook.book_id,
            NewCategoryBook.category_id == category_id
        )
    elif section_id:
        books_query = books_query.filter(
            NewBook.id == NewCategoryBook.book_id,
            NewCategoryBook.section_id == section_id
        )
    if sort_review_count and sort_review_count.isnumeric():
        if bool(int(sort_review_count)):
            books_query = books_query.order_by(NewBook.review_count.desc())
        else:
            books_query = books_query.order_by(NewBook.review_count)
    books = []
    for book in books_query.limit(end - start).offset(start).all():
        return_date = None
        old_book = Book.query.filter_by(isbn=book.isbn).first()
        if not old_book.stock_available:
            order = Order.query.filter(
                Order.book_id == old_book.id,
                cast(Order.placed_on, Date) >= cast(
                    date.today() + timedelta(days=-7), Date)
            ).order_by(Order.placed_on).first()
            if order:
                return_date = order.placed_on + timedelta(days=7)
        wishlist_count = Wishlist.query.filter_by(book_id=old_book.id).count()
        previous_count = Dump.query.filter_by(book_id=old_book.id, read_before=True).count(
        ) + Order.query.filter_by(book_id=old_book.id).count()
        books.append({
            **book.to_json(),
            "return_date": return_date,
            "wishlist_count": wishlist_count,
            "previous_count": previous_count
        })
    return jsonify({"success": True, "books": books})


@api_v2_books.route('/search-new-books')
def search_new_books():
    search_query = request.args.get('search_query')
    start = request.args.get('start')
    end = request.args.get('end')
    if not search_query or not search_query.strip():
        return jsonify({"success": False, "message": "Enter a search query"}), 400
    if len(search_query) < 3:
        return jsonify({"success": False, "message": "Search query should be atleast 3 characters long"}), 400
    if not start or not start.isnumeric():
        start = 0
    if not end or not end.isnumeric():
        end = 100
    start, end = int(start), int(end)
    books = NewBook.query.join(NewCategoryBook, NewCategory).filter(
        NewCategoryBook.category_id == NewCategory.id,
        NewCategory.name != 'Best Seller - Most Popular',
        NewCategoryBook.section_id == 1,
        or_(
            NewBook.name.ilike(f'% {search_query} %'),
            NewBook.isbn.ilike(f'%{search_query}%'),
            NewBook.authors.ilike(f'%{search_query}%'),
            NewBook.book_type.ilike(f'%{search_query}%'),
            NewBook.publisher.ilike(f'%{search_query}%'),
            NewBook.description.ilike(f'% {search_query} %'),
            NewCategory.name.ilike(f'%{search_query}%'),
        )
    ).limit(end - start).offset(start).all()
    category_to_books = dict()
    for book in books:
        categories = NewCategory.query.join(NewCategoryBook).filter(
            NewCategoryBook.section_id == 1,
            NewCategoryBook.book_id == book.id,
            NewCategory.max_age != 100,
        ).all()
        for category in categories:
            if category.name not in category_to_books:
                category_to_books[category.name] = {
                    "category": category.name,
                    "books": [],
                    "min_age": category.min_age,
                    "max_age": category.max_age,
                }
            category_to_books[category.name]["books"].append(book.to_json())
    book_set = [category_to_books[category] for category in category_to_books]
    book_set = sorted(book_set, key=lambda books: len(
        books["books"]), reverse=True)
    return jsonify({"success": True, "book_set": book_set})


@api_v2_books.route('/new-book', methods=['POST', 'PUT'])
def new_book():
    id = request.form.get('id')
    isbn = request.form.get('isbn')
    name = request.form.get('name')
    min_age = request.form.get('min_age')
    max_age = request.form.get('max_age')
    image = request.form.get('image')
    rating = request.form.get('rating')
    review_count = request.form.get('review_count')
    categories = request.form.get('categories')
    image_file = request.files.get('image')
    if not all((isbn, name, min_age, max_age, rating, review_count, categories)) or (not image and not image_file):
        return jsonify({"success": False, "message": "Provide all the data"}), 400
    if not str(min_age).isnumeric() or not str(max_age).isnumeric() or int(min_age) < 0 or int(min_age) > int(max_age):
        return jsonify({"success": False, "message": "Invalid minimum and maximum age"}), 400
    if not str(rating).replace('.', '').isnumeric() or float(rating) < 0 or float(rating) > 5:
        return jsonify({"success": False, "message": "Invalid rating"}), 400
    if not str(review_count).isnumeric() or int(review_count) < 0:
        return jsonify({"success": False, "message": "Invalid review count"}), 400
    if type(json.loads(categories)) != type([]):
        return jsonify({"success": False, "message": "Invalid category list"}), 400
    min_age = int(min_age)
    max_age = int(max_age)
    categories = json.loads(categories)
    if request.method == 'POST':
        if NewBook.query.filter_by(isbn=isbn).count():
            return jsonify({"success": False, "message": "Book with given ISBN already exists"}), 400

        book_image = image
        if not image or not image.startswith('http'):
            extension = image_file.filename.split(".")[-1]
            upload_to_aws(image_file, 'book_images',
                          f'book_images/{isbn}.{extension}')
            s3_url = os.environ.get('AWS_S3_URL')
            book_image = f'{s3_url}/book_images/{isbn}.{extension}'

        NewBook.create(
            name,
            book_image,
            isbn,
            rating,
            review_count,
            100,
            min_age,
            max_age
        )
        new_book = NewBook.query.filter_by(isbn=isbn).first()

        for category in categories:
            NewCategoryBook.create(
                category['category']['id'],
                new_book.id,
                category['section']['id'],
            )

        if not Book.query.filter_by(isbn=isbn).count():
            Book.create(
                name,
                book_image,
                isbn,
                rating,
                review_count,
                '',
                'English',
                '',
                '',
                1,
                None,
                None,
                None,
                None
            )
        book = Book.query.filter_by(isbn=isbn).first()
        book.age_group_1 = (min_age >= 0 and min_age <= 2) or (
            max_age >= 0 and max_age <= 2)
        book.age_group_2 = (min_age >= 3 and min_age <= 5) or (
            max_age >= 3 and max_age <= 5)
        book.age_group_3 = (min_age >= 6 and min_age <= 8) or (
            max_age >= 6 and max_age <= 8)
        book.age_group_4 = (min_age >= 9 and min_age <= 11) or (
            max_age >= 9 and max_age <= 11)
        book.age_group_5 = (min_age >= 12 and min_age <= 14) or (
            max_age >= 12 and max_age <= 14)
        book.age_group_6 = (min_age >= 15) or (max_age >= 15)

        db.session.commit()

        return jsonify({"success": True, "book": new_book.to_json()})
    elif request.method == 'PUT':
        new_book = NewBook.query.filter_by(id=id).first()
        if not new_book:
            return jsonify({"success": False, "message": "Invalid book ID"}), 404

        book = Book.query.filter_by(isbn=new_book.isbn).first()

        book_image = image
        if not image or not image.startswith('http'):
            extension = image_file.filename.split(".")[-1]
            upload_to_aws(image_file, 'book_images',
                          f'book_images/{isbn}.{extension}')
            s3_url = os.environ.get('AWS_S3_URL')
            book_image = f'{s3_url}/book_images/{isbn}.{extension}'

        new_book.isbn = book.isbn = isbn
        new_book.name = book.name = name
        new_book.image = book.image = book_image
        new_book.review_count = book.review_count = review_count
        new_book.rating = book.rating = rating
        new_book.min_age = min_age
        new_book.max_age = max_age

        for category in NewCategoryBook.query.filter_by(book_id=new_book.id).all():
            category.delete()
        for category in categories:
            NewCategoryBook.create(
                category['category']['id'],
                new_book.id,
                category['section']['id'],
            )

        book.age_group_1 = (min_age >= 0 and min_age <= 2) or (
            max_age >= 0 and max_age <= 2)
        book.age_group_2 = (min_age >= 3 and min_age <= 5) or (
            max_age >= 3 and max_age <= 5)
        book.age_group_3 = (min_age >= 6 and min_age <= 8) or (
            max_age >= 6 and max_age <= 8)
        book.age_group_4 = (min_age >= 9 and min_age <= 11) or (
            max_age >= 9 and max_age <= 11)
        book.age_group_5 = (min_age >= 12 and min_age <= 14) or (
            max_age >= 12 and max_age <= 14)
        book.age_group_6 = (min_age >= 15) or (max_age >= 15)

        db.session.commit()

        return jsonify({"success": True, "book": new_book.to_json()})


@api_v2_books.route('/update-book-quantity', methods=['POST'])
def update_book_quantity():
    id = request.json.get('id')
    stock_available = request.json.get('stock_available')
    rentals = request.json.get('rentals')
    if not str(stock_available).isnumeric() or not str(rentals).isnumeric() or int(stock_available) < 0 or int(rentals) < 0:
        return jsonify({"success": False, "message": "Invalid book quantity"}), 400
    new_book = NewBook.query.filter_by(id=id).first()
    if not new_book:
        return jsonify({"success": False, "message": "Invalid book ID"}), 404
    book = Book.query.filter_by(isbn=new_book.isbn).first()
    if not book:
        return jsonify({"success": False, "message": "Invalid book ID"}), 404

    book.stock_available = stock_available
    book.rentals = rentals

    db.session.commit()

    return jsonify({"success": True, "book": new_book.to_json()})


@api_v2_books.route('/delete-new-book', methods=['POST'])
def delete_new_book():
    id = request.json.get('id')
    new_book = NewBook.query.filter_by(id=id).first()
    if not new_book:
        return jsonify({"success": False, "message": "Invalid book ID"}), 404
    new_book.delete()
    return jsonify({"success": True})


@api_v2_books.route('/add-books-from-csv', methods=['POST'])
def add_books_from_csv():
    books_csv_file = request.files.get('books_csv')
    if books_csv_file.filename.split(".")[-1] != 'csv':
        return jsonify({"status": "success", "message": "Only CSV files are supported"}), 400
    filename = './temporary.csv'
    books_csv_file.save(filename)
    books = []
    with open(filename, mode="r", encoding='utf8') as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            books.append(line)
    if len(books) < 2:
        return jsonify({"status": "success", "message": "Empty CSV file"}), 400
    columns = dict()
    for i in range(len(books[0])):
        columns[str(books[0][i]).lower()] = i
    books = books[1:]
    if 'isbn' not in columns or 'name' not in columns:
        return jsonify({"status": "success", "message": "CSV file should have atleast ISBN and name column"}), 400
    added_isbns, not_added_isbns = [], []
    for book in books:
        isbn = book[columns['isbn']]
        name = book[columns['name']]
        if not isbn or not name:
            if isbn:
                not_added_isbns.append(isbn)
            continue
        rating = '5'
        price = ''
        image = ''
        review_count = 0
        min_age = 0
        max_age = 14
        price = 0.0
        for_age = None
        grade_level = None
        lexile_measure = None
        pages = 0
        dimensions = None
        publisher = None
        language = 'English'
        if 'rating' in columns:
            rating = book[columns['rating']]
        if 'review_count' in columns:
            review_count = book[columns['review_count']]
        if 'language' in columns:
            language = book[columns['language']]
        if 'price' in columns:
            price = book[columns['price']]
        if 'min_age' in columns:
            min_age = book[columns['min_age']]
        if 'max_age' in columns:
            max_age = book[columns['max_age']]
        if 'for_age' in columns:
            for_age = book[columns['for_age']]
        if 'grade_level' in columns:
            grade_level = book[columns['grade_level']]
        if 'lexile_measure' in columns:
            lexile_measure = book[columns['lexile_measure']]
        if 'pages' in columns:
            pages = book[columns['pages']]
        if 'dimensions' in columns:
            dimensions = book[columns['dimensions']]
        if 'publisher' in columns:
            publisher = book[columns['publisher']]
        if 'main_image' in columns:
            image = book[columns['main_image']]

        if not str(min_age).isnumeric() or not str(max_age).isnumeric() or int(min_age) < 0 or int(min_age) > int(max_age):
            min_age = 0
            max_age = 14
        if not str(rating).replace('.', '').isnumeric() or float(rating) < 0 or float(rating) > 5:
            rating = '5.0'
        if not str(review_count).isnumeric() or int(review_count) < 0:
            review_count = 0

        min_age = int(min_age)
        max_age = int(max_age)

        new_book = NewBook.query.filter_by(isbn=isbn).first()
        if not new_book:
            NewBook.create(
                name,
                image,
                isbn,
                rating,
                '',  # review_count
                100,
                min_age,
                max_age
            )
            new_book = NewBook.query.filter_by(isbn=isbn).first()
        new_book.name = name
        new_book.image = image
        new_book.rating = rating
        new_book.review_count = review_count
        new_book.min_age = min_age
        new_book.max_age = max_age
        new_book.price = price
        new_book.for_age = for_age
        new_book.grade_level = grade_level
        new_book.lexile_measure = lexile_measure
        new_book.pages = pages
        new_book.dimensions = dimensions
        new_book.publisher = publisher
        new_book.language = language

        for column in columns:
            if column.startswith('image') and book[columns[column]].startswith('http'):
                NewBookImage.create(book[columns[column]], new_book.id)

        old_book = Book.query.filter_by(isbn=isbn).first()
        if not old_book:
            Book.create(
                name,
                image,
                isbn,
                rating,
                review_count,
                '',
                language,
                '',
                '',
                1,
                None,
                None,
                None,
                None
            )
            old_book = Book.query.filter_by(isbn=isbn).first()

        old_book.name = name
        old_book.image = image
        old_book.rating = rating
        old_book.review_count = review_count
        old_book.language = language
        old_book.age_group_1 = (min_age >= 0 and min_age <= 2) or (
            max_age >= 0 and max_age <= 2)
        old_book.age_group_2 = (min_age >= 3 and min_age <= 5) or (
            max_age >= 3 and max_age <= 5)
        old_book.age_group_3 = (min_age >= 6 and min_age <= 8) or (
            max_age >= 6 and max_age <= 8)
        old_book.age_group_4 = (min_age >= 9 and min_age <= 11) or (
            max_age >= 9 and max_age <= 11)
        old_book.age_group_5 = (min_age >= 12 and min_age <= 14) or (
            max_age >= 12 and max_age <= 14)
        old_book.age_group_6 = (min_age >= 15) or (max_age >= 15)

        added_isbns.append(isbn)
        db.session.commit()

    os.remove(filename)
    return jsonify({"status": "success", "added_isbns": added_isbns, "not_added_isbns": not_added_isbns})
