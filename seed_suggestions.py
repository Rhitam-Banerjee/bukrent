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
    suggestions = Suggestion.query.all()
    for s in suggestions:
        s.delete()
