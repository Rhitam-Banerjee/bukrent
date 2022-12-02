from flask import Blueprint, jsonify, make_response, request

from sqlalchemy import or_

from app.models.admin import Admin
from app.models.user import Address, User, Child
from app.models.books import Book, BookAuthor, BookCategory
from app.models.buckets import DeliveryBucket, Suggestion
from app.models.order import Order
from app.models.author import Author
from app.models.publishers import Publisher
from app.models.series import Series
from app.models.format import Format
from app.models.category import Category
from app import db

import uuid

import json

from functools import wraps

from app.api_admin.utils import validate_user, token_required, upload_to_aws

import os
import jwt
from datetime import datetime, date, timedelta

api_admin = Blueprint('api_admin', __name__, url_prefix="/api_admin")

@api_admin.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    admin = Admin.query.filter_by(username=username).first()
    if not admin:
        return jsonify({
            "status": "error",
            "message": "Invalid username"
        }), 400
    if password != admin.password:
        return jsonify({
            "status": "error",
            "message": "Incorrect password"
        }), 400
    access_token_admin = jwt.encode({'id' : admin.id}, os.environ.get('SECRET_KEY'), "HS256")
    response = make_response(jsonify({
        "status": "success",
        "admin": admin.to_json(),
    }), 200)
    response.set_cookie('access_token_admin', access_token_admin, secure=True, httponly=True, samesite='None')
    return response

@api_admin.route('/refresh')
@token_required
def refresh(admin):
    return jsonify({
        "status": "success",
        "admin": admin.to_json(),
    })

@api_admin.route('/logout', methods=['POST'])
@token_required
def logout(admin):
    response = make_response(jsonify({
        "status": "success",
    }))
    response.set_cookie('access_token_admin', '', secure=True, httponly=True, samesite='None')
    return response

@api_admin.route('/get-users')
@token_required
def get_users(admin):
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))
    search = request.args.get('query')
    sort = request.args.get('sort')
    payment_status = request.args.get('payment_status')
    plan = request.args.get('plan')
    plan_duration = request.args.get('duration')

    all_users = []
    query = User.query

    if payment_status:
        if payment_status == 'Unpaid':
            query = query.filter(or_(User.payment_status == 'Unpaid', User.payment_status == None, User.payment_status == ''))
        else:
            query = query.filter_by(payment_status=payment_status)
    if plan:
        query = query.filter_by(books_per_week=plan)
    if plan_duration:
        query = query.filter_by(plan_duration=plan_duration)
    if search:
        query = query.filter(or_(
                User.first_name.ilike(f'{search}%'),
                User.last_name.ilike(f'{search}%'),
                User.mobile_number.ilike(f'{search}%')
            ))
    if sort and int(sort) == 1:
        query = query.order_by(User.id)
    else:
        query = query.order_by(User.id.desc())
    all_users = query.filter_by(is_deleted=False).limit(end - start).offset(start).all()
    users = []
    for user in all_users:
        user = User.query.get(user.id)
        users.append({
            "password": user.password,
            "wishlist": user.get_wishlist(),
            "suggestions": user.get_suggestions(),
            "previous": user.get_previous_books(),
            **user.to_json()
        })
    return jsonify({
        "status": "success",
        "users": users
    })

@api_admin.route('/get-archived-users')
@token_required
def get_archived_users(admin):
    users = User.query.filter_by(is_deleted=True).all()
    return jsonify({
        "status": "success",
        "users": [user.to_json() for user in users]
    })

@api_admin.route('/update-user', methods=['POST'])
@token_required
@validate_user
def update_user(admin):
    id = request.json.get('id')
    name = request.json.get('name')
    mobile_number = request.json.get('mobile_number')
    contact_number = request.json.get('contact_number')
    address = request.json.get('address')
    pin_code = request.json.get('pin_code')
    plan_date = request.json.get('plan_date')
    plan_duration = request.json.get('plan_duration')
    plan_id = request.json.get('plan_id')
    payment_status = request.json.get('payment_status')
    source = request.json.get('source')
    password = request.json.get('password')
    children = request.json.get('children')

    if not mobile_number: 
        return jsonify({
            "status": "error",
            "message": "Mobile number is necessary"
        }), 400

    if not id:
        return jsonify({
            "status": "error",
            "message": "Provide user ID"
        }), 400

    user = User.query.get(id)
    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400

    if name:
        user.first_name = name.split()[0]
        if len(name.split()) > 1:
            user.last_name = ' '.join(name.split()[1:])
    else: 
        user.first_name = ''
        user.last_name = ''

    user.mobile_number = mobile_number
    user.contact_number = contact_number
    user.password = password
    user.plan_duration = plan_duration
    user.source = source

    if plan_date:
        user.plan_date = datetime.strptime(plan_date, '%Y-%m-%d')
    else: 
        user.plan_date = None

    user_children = Child.query.filter_by(user_id=user.id).all()
    for child in user_children: 
        child.delete()
    if children and type(children) == type([]):
        for child in children:
            child_obj = Child.query.filter_by(name=child['name']).first()
            if not child_obj:
                user.add_child(child)
        age_groups = []
        for child in children:
            age_groups.append(child.get("age_group"))
        age_groups = list(set(age_groups))
        user.add_age_groups(age_groups)

    if plan_id:
        plan_id = int(plan_id)
    if plan_id == 1:
        user.plan_id = os.environ.get('RZP_PLAN_1_ID')
        user.books_per_week = 1
    elif plan_id == 2:
        user.plan_id = os.environ.get('RZP_PLAN_2_ID')
        user.books_per_week = 2
    elif plan_id == 4:
        user.plan_id = os.environ.get('RZP_PLAN_3_ID')
        user.books_per_week = 4

    if payment_status:
        user.payment_status = payment_status

    for user_address in user.address:
        user_address.delete()
    if address and pin_code:
        address = Address.create({"area": address, "pin_code": pin_code}, user.id)

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "User updated",
        "user": {
            "password": user.password,
            "wishlist": user.get_wishlist(),
            "suggestions": user.get_suggestions(),
            "previous": user.get_previous_books(),
            **user.to_json()
        }
    })

@api_admin.route('/add-user', methods=['POST'])
@token_required
@validate_user
def add_user(admin):
    name = request.json.get('name')
    mobile_number = request.json.get('mobile_number')
    password = request.json.get('password')
    contact_number = request.json.get('contact_number')
    address = request.json.get('address')
    pin_code = request.json.get('pin_code')
    plan_id = request.json.get('plan_id')
    payment_id = request.json.get('payment_id')
    plan_date = request.json.get('plan_date')
    plan_duration = request.json.get('plan_duration')
    source = request.json.get('source')
    payment_status = request.json.get('payment_status')
    current_books = request.json.get('current_books')
    next_books = request.json.get('next_books')
    children = request.json.get('children')
    if not all((name, mobile_number, password)):
        return jsonify({
            "status": "error",
            "message": "Fill all the fields"
        }), 400
    if not children or not len(children):
        return jsonify({
            "status": "error",
            "message": "Add atleast 1 child"
        }), 400
    if User.query.filter_by(mobile_number=mobile_number, is_deleted=False).count():
        return jsonify({
            "status": "error",
            "message": "Mobile number already exists"
        }), 400

    first_name = name.split()[0]
    last_name = ''
    if len(name.split()) > 1:
        last_name = ' '.join(name.split()[1:])
    user = User.create(first_name, last_name, mobile_number, password)
    user.contact_number = contact_number
    user.payment_id = payment_id
    user.plan_duration = plan_duration
    user.source = source
    user.payment_status = payment_status
    if plan_date:
        user.plan_date = datetime.strptime(plan_date, '%Y-%m-%d')
    if plan_id:
        plan_id = int(plan_id)
    if plan_id == 1:
        user.plan_id = os.environ.get('RZP_PLAN_1_ID')
        user.books_per_week = 1
    elif plan_id == 2:
        user.plan_id = os.environ.get('RZP_PLAN_2_ID')
        user.books_per_week = 2
    elif plan_id == 4:
        user.plan_id = os.environ.get('RZP_PLAN_3_ID')
        user.books_per_week = 4

    if address and pin_code:
        address = Address.create({"area": address, "pin_code": pin_code}, user.id)

    if children and type(children) == type([]) and len(children):
        for child in children:
            user.add_child(child)
        age_groups = []
        for child in children:
            age_groups.append(child.get("age_group"))
        age_groups = list(set(age_groups))
        user.add_age_groups(age_groups)

    bucket_size = 1
    if plan_id == os.environ.get('RZP_PLAN_2_ID'):
        bucket_size = 2
    elif plan_id == os.environ.get('RZP_PLAN_3_ID'):
        bucket_size = 4

    if len(current_books):
        user.last_delivery_date = date.today()

    for i in range(bucket_size):
        if i >= len(current_books):
            break
        book = Book.query.filter_by(isbn=current_books[i]).first()
        Order.create(user.id, book.id, None, user.last_delivery_date)

    for i in range(bucket_size):
        if i >= len(next_books):
            break
        book = Book.query.filter_by(isbn=current_books[i]).first()
        DeliveryBucket.create(user.id, book.id, None, None)

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "User updated",
        "user": {
            "password": user.password,
            "wishlist": user.get_wishlist(),
            "suggestions": user.get_suggestions(),
            "previous": user.get_previous_books(),
            **user.to_json()
        }
    })

@api_admin.route('/delete-user', methods=['POST'])
@token_required
def delete_user(admin):
    id = request.json.get('id')

    user = User.query.get(id)
    if not user or user.is_deleted:
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400

    user.is_deleted = True

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "User deleted"
    })

@api_admin.route('/restore-user', methods=['POST'])
@token_required
def restore_user(admin):
    id = request.json.get('id')

    user = User.query.get(id)
    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400

    user.is_deleted = False

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "User restored"
    })

@api_admin.route('/get-books', methods=['POST'])
@token_required
def get_books(admin):
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))
    search = request.args.get('query')
    age_group = int(request.args.get('age_group'))
    authors = request.json.get('authors')
    publishers = request.json.get('publishers')
    series = request.json.get('series')
    types = request.json.get('types')
    
    books = {}

    if search or not any((len(authors), len(publishers), len(series), len(types))): 
        if not search: 
            search = ''
        query = Book.query.filter(or_(
            Book.name.ilike(f'{search}%'),
            Book.description.ilike(f'%{search}%'),
            Book.isbn.ilike(f'{search}%')))
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
            if author_obj.to_json() in age_authors: 
                for book in author_obj.books: 
                    books[book.isbn] = book
        for publisher in publishers: 
            publisher_obj = Publisher.query.filter_by(guid=publisher).first()
            if publisher_obj.to_json() in age_publishers: 
                for book in publisher_obj.books: 
                    books[book.isbn] = book
        for serie in series: 
            serie_obj = Series.query.filter_by(guid=serie).first()
            if serie_obj.to_json() in age_series: 
                for book in serie_obj.books: 
                    books[book.isbn] = book
        for format in types: 
            format_obj = Format.query.filter_by(guid=format).first()
            if format_obj.to_json() in age_types: 
                for book in format_obj.books: 
                    books[book.isbn] = book

        books = list(books.values())[start:end]

    final_books = []
    for book in books:
        tags = []
        book_json = book.to_json()
        for tag in book_json['categories']:
            tag_obj = Category.query.filter_by(name=tag).first()
            tags.append({"guid": tag_obj.guid, "name": tag_obj.name})
        book_json['tags'] = tags
        final_books.append(book_json)

    return jsonify({
        "status": "success",
        "books": final_books
    })

@api_admin.route('/add-book', methods=['POST'])
@token_required
def add_book(admin):
    isbn = request.form.get('isbn')
    title = request.form.get('title')
    authors = request.form.get('authors')
    copies = request.form.get('copies')
    rentals = request.form.get('rentals')
    tags = request.form.get('tags')
    image = request.files.get('image')
    type = request.form.get('type')

    if not all((isbn, title)):
        return jsonify({
            "status": "error",
            "message": "ISBN and title is necessary"
        }), 400

    if type == 'add':
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
    elif type == 'add':
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

    final_book = book.to_json()
    tags = []
    for tag in final_book['categories']:
        tag_obj = Category.query.filter_by(name=tag).first()
        tags.append({"guid": tag_obj.guid, "name": tag_obj.name})
    final_book['tags'] = tags

    return jsonify({
        "status": "success",
        "book": final_book
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

@api_admin.route('/add-books-user', methods=['POST'])
@token_required
def add_books_user(admin): 
    user_id = request.json.get('user_id')
    isbn_list = request.json.get('isbn_list')
    books_type = request.json.get('type')

    if not all((user_id, isbn_list)) or type(isbn_list) != type([]): 
        return jsonify({
            "status": "error",
            "message": "Provide user ID and a list of ISBNs"
        }), 400
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    
    books_found, books_not_found = [], []
    children = Child.query.filter_by(user_id=user_id).all()
    for isbn in isbn_list: 
        book = Book.query.filter_by(isbn=isbn).first()
        if not book: 
            books_not_found.append(isbn)
        else: 
            books_found.append(isbn)
            if books_type == 'suggestions': 
                for child in children: 
                    Suggestion.create(user.id, book.id, child.age_group)
            elif books_type == 'wishlist': 
                user.add_to_wishlist(book.guid)
            elif books_type == 'previous': 
                Order.create(user.id, book.id, 0, datetime.now() - timedelta(days = 90))

    return jsonify({
        "status": "success",
        "books_found": books_found,
        "books_not_found": books_not_found,
        "user": {
            "password": user.password,
            "wishlist": user.get_wishlist(),
            "suggestions": user.get_suggestions(),
            "previous": user.get_previous_books(),
            **user.to_json()
        }
    })

@api_admin.route('/add-to-wishlist', methods=['POST'])
@token_required
def add_to_wishlist(admin): 
    book_guid = request.json.get('book_guid')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    user.add_to_wishlist(book_guid)
    return jsonify({
        "status": "success",
        "user": {
            "password": user.password,
            "wishlist": user.get_wishlist(),
            "suggestions": user.get_suggestions(),
            "previous": user.get_previous_books(),
            **user.to_json()
        }
    })

@api_admin.route('/remove-from-wishlist', methods=['POST'])
@token_required
def remove_from_wishlist(admin): 
    book_guid = request.json.get('book_guid')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    user.wishlist_remove(book_guid)
    return jsonify({
        "status": "success",
        "user": {
            "password": user.password,
            "wishlist": user.get_wishlist(),
            "suggestions": user.get_suggestions(),
            "previous": user.get_previous_books(),
            **user.to_json()
        }
    })

@api_admin.route('/remove-from-suggestions', methods=['POST'])
@token_required
def remove_from_suggestions(admin): 
    book_guid = request.json.get('book_guid')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    user.suggestion_to_dump(book_guid)
    return jsonify({
        "status": "success",
        "user": {
            "password": user.password,
            "wishlist": user.get_wishlist(),
            "suggestions": user.get_suggestions(),
            "previous": user.get_previous_books(),
            **user.to_json()
        }
    })

@api_admin.route('/remove-from-previous', methods=['POST'])
@token_required
def remove_from_previous(admin): 
    book_guid = request.json.get('book_guid')
    user_id = request.json.get('user_id')
    user = User.query.get(user_id)
    if not user: 
        return jsonify({
            "status": "error",
            "message": "Invalid user ID"
        }), 400
    user.remove_from_previous(book_guid)
    return jsonify({
        "status": "success",
        "user": {
            "password": user.password,
            "wishlist": user.get_wishlist(),
            "suggestions": user.get_suggestions(),
            "previous": user.get_previous_books(),
            **user.to_json()
        }
    })