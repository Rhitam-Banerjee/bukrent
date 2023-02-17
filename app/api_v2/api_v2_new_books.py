from flask import Blueprint, jsonify, request
import random
import json

from sqlalchemy import and_, or_

from app import db
from app.models.new_books import NewBookSection, NewBook, NewCategory, NewCategoryBook
from app.models.books import Book

from app.api_admin.utils import upload_to_aws

import os

api_v2_new_books = Blueprint('api_v2_new_books', __name__, url_prefix="/api_v2_new_books")

must_read_books = json.loads(open('./app/must-read-books.json', mode="r", encoding='utf8').read())

@api_v2_new_books.route('/get-book-set')
def get_book_set(): 
    age = request.args.get('age')
    section_name = request.args.get('section_name')
    if not section_name or age is None: 
        return jsonify({"success": False, "message": "Provide age group and section name"})
    if not str(age).isnumeric(): 
        return jsonify({"success": False, "message": "Invalid age group"})
    section = NewBookSection.query.filter_by(name=section_name).first()
    if not section: 
        return jsonify({"success": False, "message": "Invalid section name"})
    age = int(age)
    categories = NewCategory.query.filter(
        or_(
            and_(NewCategory.min_age <= age, NewCategory.max_age >= age),
            and_(NewCategory.min_age <= age + 1, NewCategory.max_age >= age + 1)
        )
    ).order_by(NewCategory.category_order).all()
    book_set = []
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
        random.shuffle(books)
        if len(books): 
            book_set.append({
                "category": category.name,
                "books": books
            })
    return jsonify({"success": True, "book_set": book_set})

@api_v2_new_books.route('/get-category-books')
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

@api_v2_new_books.route('/get-new-books')
def get_new_books(): 
    start = request.args.get('start')
    end = request.args.get('end')
    age = request.args.get('age')
    category_id = request.args.get('category_id')
    search_query = request.args.get('search_query')
    if age is None or (not str(age).isnumeric() and age != '-1'): 
        return jsonify({"success": False, "message": "Provide age group"}), 400
    if category_id and not NewCategory.query.filter_by(id=category_id).count(): 
        return jsonify({"success": False, "message": "Invalid category name"}), 400
    if not search_query: 
        search_query = ''
    if not start or not start.isnumeric(): 
        start = 0
    if not end or not end.isnumeric(): 
        end = 10
    if str(age) == '-1': 
        age = None
    else: 
        age = int(age)
    start = int(start)
    end = int(end)
    books_query = db.session.query(NewBook).filter(
        or_(
            NewBook.name.ilike(f'{search_query}%'),
            NewBook.isbn.ilike(f'{search_query}%')
        )
    )
    if age is not None: 
        books_query = books_query.filter(
            or_(
                and_(NewBook.min_age <= age, NewBook.max_age >= age),
                and_(NewBook.min_age <= age + 1, NewBook.max_age >= age + 1)
            )
        )
    if category_id: 
        books_query = books_query.filter(
            NewBook.id == NewCategoryBook.book_id,
            NewCategoryBook.category_id == category_id,
        )
    books = [book.to_json() for book in books_query.order_by(NewBook.book_order).limit(end - start).offset(start).all()]
    return jsonify({"success": True, "books": books})

@api_v2_new_books.route('/get-categories')
def get_categories(): 
    age = request.args.get('age')
    start = request.args.get('start')
    end = request.args.get('end')
    if not start or not start.isnumeric(): 
        start = 0
    if not end or not end.isnumeric(): 
        end = 10
    start = int(start)
    end = int(end)
    categories_query = NewCategory.query
    if age is not None and age.isnumeric(): 
        age = int(age)
        categories_query = categories_query.filter(
            or_(
                and_(NewCategory.min_age <= age, NewCategory.max_age >= age),
                and_(NewCategory.min_age <= age + 1, NewCategory.max_age >= age + 1)
            )
        )
    categories = [category.to_json() for category in categories_query.order_by(NewCategory.category_order).limit(end - start).offset(start).all()]
    return jsonify({"success": True, "categories": categories})

@api_v2_new_books.route('/new-book', methods=['POST', 'PUT'])
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
    if not all((id, isbn, name, min_age, max_age, image, rating, review_count, categories)): 
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
        if NewBook.query.filter_by(isbn=isbn).count() or Book.query.filter_by(isbn=isbn).count(): 
            return jsonify({"success": False, "message": "Book with given ISBN already exists"}), 400
        
        book_image = image
        if not image.startswith('http'): 
            extension = image.filename.split(".")[-1]
            upload_to_aws(image, 'book_images', f'book_images/{isbn}.{extension}')
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

        Book.create(
            name, 
            book_image, 
            isbn, 
            rating, 
            review_count, 
            None, 
            'English', 
            None, 
            None, 
            1, 
            None, 
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
        
        new_book = NewBook.query.filter_by(isbn=isbn).first()

        return jsonify({"success": True, "book": new_book.to_json()})
    elif request.method == 'PUT': 
        new_book = NewBook.query.filter_by(id=id).first()
        if not new_book: 
            return jsonify({"success": False, "message": "Invalid book ID"}), 404
        
        book = Book.query.filter_by(isbn=new_book.isbn).first()

        book_image = image
        if not image.startswith('http'): 
            extension = image.filename.split(".")[-1]
            upload_to_aws(image, 'book_images', f'book_images/{isbn}.{extension}')
            s3_url = os.environ.get('AWS_S3_URL')
            book_image = f'{s3_url}/book_images/{isbn}.{extension}'

        new_book.isbn = book.isbn = isbn
        new_book.name = book.name = name
        new_book.image = book.image = book_image
        new_book.review_count = book.review_count = review_count
        new_book.rating = book.rating = rating
        new_book.min_age = min_age
        new_book.max_age = max_age

        book.age_group_1 = (min_age >= 0 and min_age <= 2) or (max_age >= 0 and max_age <= 2)
        book.age_group_2 = (min_age >= 3 and min_age <= 5) or (max_age >= 3 and max_age <= 5)
        book.age_group_3 = (min_age >= 6 and min_age <= 8) or (max_age >= 6 and max_age <= 8)
        book.age_group_4 = (min_age >= 9 and min_age <= 11) or (max_age >= 9 and max_age <= 11)
        book.age_group_5 = (min_age >= 12 and min_age <= 14) or (max_age >= 12 and max_age <= 14)
        book.age_group_6 = (min_age >= 15) or (max_age >= 15)

        db.session.commit()

        return jsonify({"success": True, "book": new_book.to_json()})