from flask import jsonify, request

from sqlalchemy import or_

from app.models.books import Book, BookAuthor, BookCategory
from app.models.author import Author
from app.models.publishers import Publisher
from app.models.series import Series
from app.models.format import Format
from app.models.category import Category
from app import db

import uuid
import json
import csv

from app.api_admin.utils import api_admin, token_required, upload_to_aws

import os

@api_admin.route('/get-books', methods=['POST'])
@token_required
def get_books(admin):
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))
    search = request.args.get('query')
    age_group = int(request.args.get('age_group'))
    amazon_bestseller = request.args.get('amazon_bestseller')
    most_borrowed = request.args.get('most_borrowed')
    authors = request.json.get('authors')
    publishers = request.json.get('publishers')
    series = request.json.get('series')
    types = request.json.get('types')

    if amazon_bestseller and str(amazon_bestseller).isnumeric(): 
        amazon_bestseller = int(amazon_bestseller)
    if most_borrowed and str(most_borrowed).isnumeric(): 
        most_borrowed = int(most_borrowed)
    
    books = {}

    if search or not any((len(authors), len(publishers), len(series), len(types))): 
        if not search: 
            search = ''
        query = Book.query.filter(or_(
            Book.name.ilike(f'{search}%'),
            Book.description.ilike(f'%{search}%'),
            Book.isbn.ilike(f'{search}%')
        ))
        if most_borrowed: 
            query = query.filter_by(most_borrowed=True)
        if amazon_bestseller: 
            query = query.filter_by(amazon_bestseller=True)
        if age_group == 1: 
            query = query.filter_by(age_group_1=True)
        elif age_group == 2:
            query = query.filter_by(age_group_2=True)
        elif age_group == 3:
            query = query.filter_by(age_group_3=True)
        elif age_group == 4:
            query = query.filter_by(age_group_4=True)
        elif age_group == 5:
            query = query.filter_by(age_group_5=True)
        elif age_group == 6:
            query = query.filter_by(age_group_6=True)
        books = query.limit(end - start).offset(start).all()
    else: 
        age_authors = Author.get_authors(age_group, 0, 10000)
        age_publishers = Publisher.get_publishers(age_group, 0, 10000)
        age_series = Series.get_series(age_group, 0, 10000)
        age_types = Format.get_types(age_group, 0, 10000)
        
        for author in authors: 
            author_obj = Author.query.filter_by(guid=author).first()
            if author_obj and author_obj.to_json() in age_authors: 
                for book in author_obj.books: 
                    books[book.isbn] = book
        for publisher in publishers: 
            publisher_obj = Publisher.query.filter_by(guid=publisher).first()
            if publisher_obj and publisher_obj.to_json() in age_publishers: 
                for book in publisher_obj.books: 
                    books[book.isbn] = book
        for serie in series: 
            serie_obj = Series.query.filter_by(guid=serie).first()
            if serie_obj and serie_obj.to_json() in age_series: 
                for book in serie_obj.books: 
                    books[book.isbn] = book
        for format in types: 
            format_obj = Format.query.filter_by(guid=format).first()
            if format_obj and format_obj.to_json() in age_types: 
                for book in format_obj.books: 
                    books[book.isbn] = book

        books = list(books.values())[start:end]

    return jsonify({
        "status": "success",
        "books": admin.get_books(books)
    })

@api_admin.route('/add-book', methods=['POST'])
@token_required
def add_book(admin):
    isbn = request.form.get('isbn')
    title = request.form.get('title')
    authors = request.form.get('authors')
    copies = request.form.get('copies')
    rentals = request.form.get('rentals')
    age_groups = request.form.get('age_groups')
    tags = request.form.get('tags')
    image = request.files.get('image')
    req_type = request.form.get('type')

    if not all((isbn, title)):
        return jsonify({
            "status": "error",
            "message": "ISBN and title is necessary"
        }), 400

    if not rentals: 
        rentals = 0
    if not copies: 
        copies = 0
    if req_type == 'add':
        if Book.query.filter_by(isbn=isbn).count():
            return jsonify({
                "status": "error",
                "message": "Existing ISBN"
            }), 400
        book = Book()
        book.guid = str(uuid.uuid4())
        book.review_count = 0
        book.book_format = ''
        book.language = ''
        book.description = ''
        book.rentals = 0
        book.stock_available = 0
    else:
        if not Book.query.filter_by(isbn=isbn).count():
            return jsonify({
                "status": "error",
                "message": "Invalid ISBN"
            }), 400
        book = Book.query.filter_by(isbn=isbn).first()
        book_json = book.to_json()
        for author in book_json['authors']:
            author_obj = Author.query.filter_by(name=author).first()
            book_author = BookAuthor.query.filter_by(book_id=book.id, author_id=author_obj.id).first()
            db.session.delete(book_author)
        for tag in book_json['categories']:
            tag = Category.query.filter_by(name=tag).first()
            book_category = BookCategory.query.filter_by(book_id=book.id, category_id=tag.id).first()
            db.session.delete(book_category)

    if image:
        extension = image.filename.split(".")[-1]
        upload_to_aws(image, 'book_images', f'book_images/{isbn}.{extension}')
        s3_url = os.environ.get('AWS_S3_URL')
        book.image = f'{s3_url}/book_images/{isbn}.{extension}'
    elif req_type == 'add':
        book.image = ''

    book.isbn = isbn
    book.name = title
    book.stock_available = copies
    book.rentals = rentals

    db.session.add(book)

    if authors:
        authors = json.loads(authors)
        for author in authors:
            if author:
                author_obj = Author.query.filter(Author.name.ilike(author)).first()
                if not author_obj:
                    author_obj = Author()
                    author_obj.name = author
                    author_obj.guid = str(uuid.uuid4())
                    author_obj.author_type = 'author'
                    author_obj.total_books = 0
                    db.session.add(author_obj)
                    db.session.commit()
                    author_obj = Author.query.filter_by(name=author).first()
                author_obj.total_books += 1
                book_author = BookAuthor()
                book_author.book_id = book.id
                book_author.author_id = author_obj.id
                db.session.add(book_author)
    
    if age_groups: 
        age_groups = json.loads(age_groups)
        if type(age_groups) == type([]): 
            for i in range(len(age_groups)): 
                if i == 0: 
                    book.age_group_1 = bool(age_groups[i])
                elif i == 1: 
                    book.age_group_2 = bool(age_groups[i])
                elif i == 2: 
                    book.age_group_3 = bool(age_groups[i])
                elif i == 3: 
                    book.age_group_4 = bool(age_groups[i])
                elif i == 4: 
                    book.age_group_5 = bool(age_groups[i])
                elif i == 5: 
                    book.age_group_6 = bool(age_groups[i])
    if tags:
        tags = json.loads(tags)
        for tag in tags:
            tag_obj = Category.query.filter_by(guid=tag).first()
            if not tag_obj:
                return jsonify({
                    "status": "error",
                    "message": "Invalid tag"
                }), 400
            book_category = BookCategory()
            book_category.book_id = book.id
            book_category.category_id = tag_obj.id
            db.session.add(book_category)

    db.session.commit()

    return jsonify({
        "status": "success",
        "book": admin.get_books([book])[0]
    })

@api_admin.route('/delete-book', methods=['POST'])
@token_required
def delete_book(admin): 
    guid = request.json.get('guid')
    book = Book.query.filter_by(guid=guid).first()
    if not book: 
        return jsonify({
            "status": "error",
            "message": "Invalid book ID"
        }), 400
    book.delete()
    return jsonify({"status": "success"})

@api_admin.route('/get-filters')
@token_required
def get_filters(admin):
    age_group = int(request.args.get('age_group'))
    filter_limit = int(request.args.get('filter_limit'))

    if not age_group:
        age_group = 0

    authors = Author.get_authors(age_group, 0, filter_limit)
    publishers = Publisher.get_publishers(age_group, 0, filter_limit)
    series = Series.get_series(age_group, 0, filter_limit)
    types = Format.get_types(age_group, 0, filter_limit)
    tags = Category.query.all()

    return jsonify({
        "status": "success",
        "authors": authors,
        "publishers": publishers,
        "series": series,
        "types": types,
        "tags": [tag.to_json() for tag in tags]
    })

@api_admin.route('/add-books-from-csv', methods=['POST'])
@token_required
def add_books_from_csv(admin): 
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
    print(f'Parsing {len(books)} book(s)')
    for book in books: 
        isbn = book[columns['isbn']]
        name = book[columns['name']]
        print(f'Parsing book - {isbn}')
        if not isbn or not name or Book.query.filter_by(isbn=isbn).count(): 
            if isbn: 
                print(f'marked as not added')
                not_added_isbns.append(isbn)
            continue
        rating = '5'
        book_format = ''
        language = 'English'
        price = ''
        description = ''
        stock_available = 1
        if 'rating' in columns: 
            rating = book[columns['rating']]
        if 'book_format' in columns: 
            book_format = book[columns['book_format']]
        if 'language' in columns: 
            language = book[columns['language']]
        if 'price' in columns: 
            price = book[columns['price']]
        if 'description' in columns: 
            description = book[columns['description']]
        if 'stock_available' in columns: 
            val = book[columns['stock_available']]
            if val.isnumeric() and int(val) >= 0: 
                stock_available = int(val)
        print('set book details')
        Book.create(
            name, #name
            '', #image 
            isbn, #isbn
            rating, #rating
            '', #review_count
            book_format, #book_format
            language, #language
            price, #price
            description, #description
            stock_available, #stock_available
            None, #series_id
            None, #bestseller_json
            None, #borrowed_json
            None, #suggestion_json
        )
        print('created book db')
        book = Book.query.filter_by(isbn=isbn).first()
        if 'age_group_1' in columns: 
            book.age_group_1 = bool(book[columns['age_group_1']])
        if 'age_group_2' in columns: 
            book.age_group_2 = bool(book[columns['age_group_2']])
        if 'age_group_3' in columns: 
            book.age_group_3 = bool(book[columns['age_group_3']])
        if 'age_group_4' in columns: 
            book.age_group_4 = bool(book[columns['age_group_4']])
        if 'age_group_5' in columns: 
            book.age_group_5 = bool(book[columns['age_group_5']])
        if 'age_group_6' in columns: 
            book.age_group_6 = bool(book[columns['age_group_6']])
        print('updated age groups')
        added_isbns.append(isbn)
        db.session.commit()
    os.remove(filename)
    print('removed temporary csv')
    return jsonify({"status": "success", "added_isbns": added_isbns, "not_added_isbns": not_added_isbns})