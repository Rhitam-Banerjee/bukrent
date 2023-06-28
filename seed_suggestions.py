from app import create_app, db
from app.models.user import User
from app.models.books import Book
from app.models.buckets import Suggestion
from app.models.new_books import NewBook, NewCategoryBook
from sqlalchemy import select, desc
from app.models.order import Order
from datetime import date
from random import choice

app = create_app()
db.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/bukrent'


with app.app_context():
    db.create_all()
    users = User.query.all()
    books_ids = select(NewCategoryBook.book_id).filter(
        NewCategoryBook.section_id.in_([3, 4, 5]))
    books = NewBook.query.filter(NewBook.id.in_(books_ids)).order_by(
        desc(NewBook.review_count), desc(NewBook.rating)).all()

    for u in users:
        previous = u.get_previous_books()
        if previous:
            previous = choice(previous)
            book = Book.query.filter(Book.isbn == previous['isbn']).first()
            Suggestion.create(u.id, book.id)
        for x in books[:9]:
            Suggestion.create(u.id, x.id)
