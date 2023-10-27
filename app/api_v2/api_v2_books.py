from datetime import date, timedelta
from sqlalchemy import update
import openpyxl
from flask import jsonify, request
import random
import json

from sqlalchemy import Date, Integer, and_, cast, desc, or_, table,desc, asc, nullslast
from sqlalchemy.inspection import inspect
from app import db
from app.models.new_books import NewBookImage, NewBookSection, NewBook, NewCategory, NewCategoryBook
from app.models.order import Order
from app.models.buckets import Wishlist, Dump
from app.models.books import Book

from app.api_admin.utils import upload_to_aws
from app.api_v2.utils import api_v2_books

import os
import csv

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
            books = sorted(books, key=lambda book: int(book['review_count']), reverse=True)
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
    books = sorted(books, key=lambda book: int(book.review_count), reverse=True)[:count]
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
    categories = NewCategory.query.join(NewCategoryBook).filter(NewCategoryBook.section_id == section.id).all()
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
            books_query = books_query.join(Book, NewBook.isbn == Book.isbn).filter(Book.stock_available >= 1)
        books = books_query.order_by(desc(cast(NewBook.review_count, Integer))).all()
        category_to_books = dict()
        for book in books: 
            categories = NewCategory.query.join(NewCategoryBook).filter(
                NewCategoryBook.section_id == 1,
                NewCategoryBook.book_id == book.id,
                NewCategory.max_age != 100,
            ).all()
            for category in categories: 
                if category.name not in category_to_books: 
                    category_to_books[category.name] = {"category": category.name, "books": []}
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
                books_query = books_query.join(Book, NewBook.isbn == Book.isbn).filter(Book.stock_available >= 1)
            books_all = books_query.order_by(desc(cast(NewBook.review_count, Integer))).all()
            books = []
            category_ids = set()
            for book in books_all: 
                book_categories = NewCategoryBook.query.filter_by(book_id=book.id, section_id=1).all()
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
    book_set = sorted(book_set, key=lambda category: sum([int(book.review_count) for book in category["books"]]), reverse=True)[:category_count]
    if randomize_categories: 
        random.shuffle(book_set)
    for i in range(category_count): 
        book_set[i]["books"] = [book.to_json() for book in book_set[i]["books"]]
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
    
    if age and not age.isnumeric() and age != '-1': 
        return jsonify({"success": False, "message": "Provide a valid age group"}), 400
    
    if category_id and not NewCategory.query.filter_by(id=category_id).first(): 
        return jsonify({"success": False, "message": "Invalid category ID"}), 400
    
    if section_id and not NewBookSection.query.filter_by(id=section_id).first(): 
        return jsonify({"success": False, "message": "Invalid section ID"}), 400
    
    if not search_query: 
        search_query = ''
    
    if not start or not start.isnumeric(): 
        start = 0
    
    if not end or not end.isnumeric(): 
        end = 10
    
    age = int(age) if age and age != '-1' else None
    start, end = int(start), int(end)
    
    books_query = db.session.query(NewBook)
    
    if search_query:
        # Use outerjoin with the appropriate onclause
        books_query = books_query.outerjoin(
            NewCategoryBook, 
            NewCategoryBook.book_id == NewBook.id  # Correct the onclause
        ).outerjoin(
            NewCategory,
            NewCategory.id == NewCategoryBook.category_id  # Correct the onclause
        ).filter(
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
    
    # Sorting based on your criteria
    books_query = books_query.order_by(
        nullslast(desc(NewBook.book_order)),
        nullslast(asc(NewBook.publication_date)),
        asc(NewBook.review_count)
    )
    
    books = []
    
    for book in books_query.limit(end - start).offset(start).all():
        return_date = None
        old_book = Book.query.filter_by(isbn=book.isbn).first()
        
        if not old_book.stock_available: 
            order = Order.query.filter(
                Order.book_id == old_book.id,
                cast(Order.placed_on, Date) >= cast(date.today() + timedelta(days=-7), Date)
            ).order_by(Order.placed_on).first()
            
            if order:
                return_date = order.placed_on + timedelta(days=7)
        
        wishlist_count = Wishlist.query.filter_by(book_id=old_book.id).count()
        previous_count = Dump.query.filter_by(book_id=old_book.id, read_before=True).count() + \
                         Order.query.filter_by(book_id=old_book.id).count()
        
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
    book_set = sorted(book_set, key=lambda books: len(books["books"]), reverse=True)
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
    accepted_books = {'csv', 'xlsx'}
    ext = books_csv_file.filename.split(".")[-1]
    if ext not in accepted_books:
        return jsonify({"status": "success", "message": "Only CSV files are supported"}), 400
    if ext == 'csv':
        filename = './temporary.csv'
    else:
        filename = './temporary.xlsx'
    books_csv_file.save(filename)
    books = []
    if ext == 'csv':
        with open(filename, mode="r", encoding='utf-8-sig') as file:
            iterator = csv.reader(file)
            header_row = next(iterator)
            header_row = {i: header_row[i].lower() for i in range(len(header_row))}
            for line in iterator:
                temp = {}
                for value in range(len(list(line))):
                    temp[header_row[value]] = line[value]
                if temp:
                    books.append(temp)
    else:
        workbook = openpyxl.load_workbook(filename)
        sheet = workbook.active
        iterator = sheet.iter_rows()
        header_row = next(iterator)
        header_row = {i: header_row[i].value.lower() for i in range(len(header_row))}
        for row in iterator:
            temp = {}
            for cell in range(len(row)):
                if row[cell].value:
                    temp[header_row[cell]] = row[cell].value
            if temp:
                books.append(temp)
    if len(books) < 2:
        return jsonify({"status": "success", "message": "Empty CSV file"}), 400
    if 'isbn' not in header_row.values() or 'name' not in header_row.values():
        return jsonify({"status": "success", "message": "CSV file should have atleast ISBN and name column"}), 400
    added_isbns, not_added_isbns = [], []

    inspect_new_book_object = inspect(NewBook)
    inspect_book_object = inspect(Book)
    new_book_columns = [c_attr.key for c_attr in inspect_new_book_object.mapper.column_attrs]
    book_columns = [c_attr.key for c_attr in inspect_book_object.mapper.column_attrs]
    for book in books:
        for x in book:
            if isinstance(book[x], float) or (isinstance(book[x], str) and book[x].isnumeric()):
                book[x] = int(book[x])

        if 'isbn' not in book or 'name' not in book:
            continue
        isbn = book['isbn']

        book_attr = {key: value for key, value in book.items() if key in book_columns}
        new_book_attr = {key: value for key, value in book.items() if key in new_book_columns}
        fetch_book = NewBook.query.filter_by(isbn=isbn).first()
        if fetch_book:
            update_new_book = update(NewBook).where(NewBook.isbn == isbn).values(**new_book_attr)
            db.engine.execute(update_new_book)
            update_book = update(Book).where(Book.isbn == isbn).values(**book_attr)
            db.engine.execute(update_book)
            added_isbns.append(isbn)
            db.session.commit()
            print("ADDED")
        else:
            not_added_isbns.append(isbn)
    try:
        os.remove(filename)
    except Exception as e:
        print(e)

    return jsonify({"status": "success", "added_isbns": added_isbns, "not_added_isbns": not_added_isbns})

@api_v2_books.route('/getBookAuthor', methods=['GET'])
def get_book_author():
    isbn = request.args.get('isbn')

    if not isbn:
        return jsonify({'error': 'ISBN not provided'}), 400

    # Query the database to find the book with the provided ISBN.
    book = NewBook.query.filter_by(isbn=isbn).first()

    if not book:
        return jsonify({'error': 'Book not found'}), 404

    # Split the authors by comma and create a list of author names.
    authors = book.authors.split(', ')

    # Query the database to find books with at least one of the authors in the list.
    related_books = NewBook.query.filter(NewBook.authors.in_(authors)).all()

    # Create a list of book details (author, rating, review count, ISBN, description).
    book_details = [
        {
            'name':book.name,
            'author': book.authors,
            'rating': book.rating,
            'review_count': book.review_count,
            'isbn': book.isbn,
            'description': book.description,
            'image':book.image,
        }
        for book in related_books
    ]

    return jsonify({'author': authors, 'related_books': book_details})

@api_v2_books.route('/getBooksByCategory', methods=['GET'])
def get_books_by_category():
    category_name = request.args.get('category_name')

    if not category_name:
        return jsonify({'error': 'Category name not provided'}), 400

    # Query the database to find the category by name.
    category = NewCategory.query.filter_by(name=category_name).first()

    if not category:
        return jsonify({'error': 'Category not found'}), 404

    # Query the database to find books with the specified category.
    books_in_category = NewBook.query.join(
        NewCategoryBook, NewCategoryBook.book_id == NewBook.id
    ).filter(NewCategoryBook.category_id == category.id).all()

    # Create a list of book details (name, author, rating, review count, ISBN, description).
    book_details = []
    for book in books_in_category:
        authors = book.authors.split(', ') if book.authors else []  # Handle 'authors' attribute gracefully
        book_details.append({
            'name': book.name,
            'authors': authors,
            'rating': book.rating,
            'review_count': book.review_count,
            'isbn': book.isbn,
            'description': book.description,
            'image': book.image,
            'book_order': book.book_order,
            'publication_date': book.publication_date.strftime('%Y-%m-%d') if book.publication_date else None
        })

    book_details = sorted(book_details, key=lambda x: (x['book_order'], x['publication_date'] or ''))

    return jsonify({'category_name': category_name, 'books_in_category': book_details})



@api_v2_books.route('/getBookDetails', methods=['GET'])
def get_book_details():
    isbn = request.args.get('isbn')

    if not isbn:
        return jsonify({'error': 'ISBN not provided'}), 400

    # Query the database to find the book with the provided ISBN.
    book = NewBook.query.filter_by(isbn=isbn).first()

    if not book:
        return jsonify({'error': 'Book not found'}), 404

    # Create a dictionary with all book details.
    book_details = {
        'name': book.name,
        'author': book.authors,
        'rating': book.rating,
        'review_count': book.review_count,
        'isbn': book.isbn,
        'description': book.description,
        'price': book.price,
        'for_age': book.for_age,
        'grade_level': book.grade_level,
        'lexile_measure': book.lexile_measure,
        'pages': book.pages,
        'dimensions': book.dimensions,
        'publisher': book.publisher,
        'publication_date': book.publication_date.strftime('%Y-%m-%d') if book.publication_date else None,
        'language': book.language,
    }

    return jsonify({'book_details': book_details})

@api_v2_books.route('/getAuthorsByISBN', methods=['GET'])
def get_authors_by_isbn():
    isbn = request.args.get('isbn')

    if not isbn:
        return jsonify({'error': 'ISBN not provided'}), 400

    # Query the database to find the book with the provided ISBN.
    book = NewBook.query.filter_by(isbn=isbn).first()

    if not book:
        return jsonify({'error': 'Book not found'}), 404

    # Split the authors by comma and create a list of author names.
    authors = book.authors.split(', ')

    return jsonify({'isbn': isbn, 'authors': authors})

@api_v2_books.route('/getBooksByAuthor', methods=['GET'])
def get_books_by_author():
    author_name = request.args.get('author')

    if not author_name:
        return jsonify({'error': 'Author name not provided'}), 400

    # Query the database to find books with the provided author's name.
    author_name = author_name.strip()  # Remove leading/trailing spaces
    books = NewBook.query.filter(NewBook.authors.ilike(f'%{author_name}%')).all()

    if not books:
        return jsonify({'error': 'No books found for the author'}), 404

    # Create a list of book details with author names as an array.
    book_details = [
        {
            'name': book.name,
            'authors': book.authors.split(', '),  # Convert authors to an array
            'isbn': book.isbn,
            'rating': book.rating,
            'review_count': book.review_count,
            'description': book.description,
            'image': book.image,
        }
        for book in books
    ]
    book_details = sorted(book_details, key=lambda x: int(x['review_count']), reverse=True)

    return jsonify({'author': author_name, 'books': book_details})

@api_v2_books.route('/get-books-by-genre')
def get_books_by_genre():
    genre = request.args.get('genre')
    if not genre:
        return jsonify({"success": False, "message": "Genre parameter is required."}), 400

    # Query NewBook records with a specific genre
    books = NewBook.query.filter(NewBook.genre.ilike(f'%{genre}%')).all()

    book_details = []
    for book in books:
        stock_available, rentals = 0, 0
        book_record = Book.query.filter_by(isbn=book.isbn).first()
        if book_record:
            stock_available = book_record.stock_available
            rentals = book_record.rentals

        authors = book.authors.split(', ') if book.authors else []  # Handle the case where 'authors' is None

        book_details.append({
            "id": book.id,
            "guid": book.guid,
            "name": book.name,
            "image": book.image,
            "isbn": book.isbn,
            "rating": book.rating,
            "review_count": book.review_count,
            "book_order": book.book_order,
            "min_age": book.min_age,
            "max_age": book.max_age,
            "genre": book.genre,
            "price": book.price,
            "for_age": book.for_age,
            "lexile_measure": book.lexile_measure,
            "grade_level": book.grade_level,
            "pages": book.pages,
            "dimensions": book.dimensions,
            "publisher": book.publisher,
            "publication_date": book.publication_date,
            "language": book.language,
            "description": book.description,
            "categories": [category.to_json() for category in NewCategoryBook.query.filter_by(book_id=book.id).all()],
            "images": [image.to_json() for image in NewBookImage.query.filter_by(book_id=book.id).all()],
            "stock_available": stock_available,
            "rentals": rentals,
            "authors": authors  # 'authors' list with default value or empty list
        })

    return jsonify({"success": True, "books": book_details})
