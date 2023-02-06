from flask import Blueprint, jsonify, request

from sqlalchemy import and_, or_

from app import db
from app.models.new_books import NewBook

api_v2_new_books = Blueprint('api_v2_new_books', __name__, url_prefix="/api_v2_new_books")

@api_v2_new_books.route('/get-books')
def get_books(): 
    age = request.args.get('age')
    if age is None or not str(age).isnumeric(): 
        return jsonify({"success": False, "message": "Provide age group"})
    age = int(age)
    categories = [category[0] for category in db.session.query(NewBook.category).filter(
        or_(
            and_(NewBook.min_age <= age, NewBook.max_age >= age),
            and_(NewBook.min_age <= age + 1, NewBook.max_age >= age + 1)
        )
    ).distinct().all()]
    book_set = []
    for category in categories: 
        books = NewBook.query.filter_by(category=category).order_by(NewBook.book_order).all()
        book_set.append({
            "category": category, 
            "category_order": books[0].category_order, 
            "books": [book.to_json() for book in books]
        })
    book_set = sorted(book_set, key=lambda books: books['category_order']) 
    return jsonify({"success": True, "book_set": book_set})