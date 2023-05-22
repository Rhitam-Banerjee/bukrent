from flask import jsonify, request
import random
import json

from sqlalchemy import and_, or_

from app import db
from app.models.new_books import NewBookImage, NewBookSection, NewBook, NewCategory, NewCategoryBook
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
        or_(
            # and_(NewCategory.min_age <= age, NewCategory.max_age >= age),
            and_(NewCategory.min_age <= age + 1, NewCategory.max_age >= age + 1)
        )
    ).order_by(NewCategory.category_order)
    if start is not None and end is not None: 
        categories_query = categories_query.limit(end - start).offset(start)
    categories = categories_query.all()
    book_set = []
    shuffled_categories = categories[1:]
    random.shuffle(shuffled_categories)
    categories = [categories[0], *shuffled_categories]
    for category in categories: 
        books = db.session.query(NewBook, NewCategoryBook).filter(
            NewBook.id == NewCategoryBook.book_id,
            NewCategoryBook.category_id == category.id,
            NewCategoryBook.section_id == section.id,
            or_(
                and_(NewBook.min_age <= age, NewBook.max_age >= age),
                and_(NewBook.min_age <= age + 1, NewBook.max_age >= age + 1)
            )
        ).all()
        books = [book[0].to_json() for book in books]
        if category.name == 'Best Seller - Most Popular': 
            random.shuffle(books)
        else: 
            books = sorted(books, key=lambda book: int(book['review_count']), reverse=True)
        if len(books): 
            book_set.append({
                "category": category.name,
                "books": books
            })
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
    start = int(start)
    end = int(end)
    print(search_query)
    books_query = db.session.query(NewBook).join(NewCategoryBook, NewCategory).filter(
        or_(
            NewBook.name.ilike(f'{search_query}%'),
            NewBook.isbn.ilike(f'{search_query}%'),
            NewCategory.name.ilike(f'{search_query}%'),
        )
    )
    if age is not None: 
        books_query = books_query.filter(
            or_(
                and_(NewBook.min_age <= age, NewBook.max_age >= age),
                and_(NewBook.min_age <= age + 1, NewBook.max_age >= age + 1)
            )
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
    books = [book.to_json() for book in books_query.order_by(NewBook.book_order).limit(end - start).offset(start).all()]
    return jsonify({"success": True, "books": books})

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
            upload_to_aws(image_file, 'book_images', f'book_images/{isbn}.{extension}')
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
        book.age_group_1 = (min_age >= 0 and min_age <= 2) or (max_age >= 0 and max_age <= 2)
        book.age_group_2 = (min_age >= 3 and min_age <= 5) or (max_age >= 3 and max_age <= 5)
        book.age_group_3 = (min_age >= 6 and min_age <= 8) or (max_age >= 6 and max_age <= 8)
        book.age_group_4 = (min_age >= 9 and min_age <= 11) or (max_age >= 9 and max_age <= 11)
        book.age_group_5 = (min_age >= 12 and min_age <= 14) or (max_age >= 12 and max_age <= 14)
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
            upload_to_aws(image_file, 'book_images', f'book_images/{isbn}.{extension}')
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

        book.age_group_1 = (min_age >= 0 and min_age <= 2) or (max_age >= 0 and max_age <= 2)
        book.age_group_2 = (min_age >= 3 and min_age <= 5) or (max_age >= 3 and max_age <= 5)
        book.age_group_3 = (min_age >= 6 and min_age <= 8) or (max_age >= 6 and max_age <= 8)
        book.age_group_4 = (min_age >= 9 and min_age <= 11) or (max_age >= 9 and max_age <= 11)
        book.age_group_5 = (min_age >= 12 and min_age <= 14) or (max_age >= 12 and max_age <= 14)
        book.age_group_6 = (min_age >= 15) or (max_age >= 15)

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
                '', #review_count
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
        old_book.age_group_1 = (min_age >= 0 and min_age <= 2) or (max_age >= 0 and max_age <= 2)
        old_book.age_group_2 = (min_age >= 3 and min_age <= 5) or (max_age >= 3 and max_age <= 5)
        old_book.age_group_3 = (min_age >= 6 and min_age <= 8) or (max_age >= 6 and max_age <= 8)
        old_book.age_group_4 = (min_age >= 9 and min_age <= 11) or (max_age >= 9 and max_age <= 11)
        old_book.age_group_5 = (min_age >= 12 and min_age <= 14) or (max_age >= 12 and max_age <= 14)
        old_book.age_group_6 = (min_age >= 15) or (max_age >= 15)

        added_isbns.append(isbn)
        db.session.commit()

    os.remove(filename)
    return jsonify({"status": "success", "added_isbns": added_isbns, "not_added_isbns": not_added_isbns})
