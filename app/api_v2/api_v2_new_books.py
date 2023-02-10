from flask import Blueprint, jsonify, request

import random

from sqlalchemy import and_, or_

from app import db
from app.models.new_books import NewBook, NewCategory, NewCategoryBook

api_v2_new_books = Blueprint('api_v2_new_books', __name__, url_prefix="/api_v2_new_books")

@api_v2_new_books.route('/get-book-set')
def get_book_set(): 
    age = request.args.get('age')
    if age is None or not str(age).isnumeric(): 
        return jsonify({"success": False, "message": "Provide age group"})
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
            or_(
                and_(NewBook.min_age <= age, NewBook.max_age >= age),
                and_(NewBook.min_age <= age + 1, NewBook.max_age >= age + 1)
            )
        ).all()
        books = [book[0].to_json() for book in books]
        random.shuffle(books)
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