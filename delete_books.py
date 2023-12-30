from app import create_app, db
from app.models.new_books import NewBook, Book, NewCategory, NewCategoryBook, NewBookSection
import csv

app = create_app()
db.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/bukrent'

with app.app_context():
    csv_file_path = '/home/ubuntu/bukrent/Books.csv'

    with open(csv_file_path, 'r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        for row in csv_reader:
            isbn = row[0]

            books_to_delete = Book.query.filter_by(isbn=isbn).all()
            new_books_to_delete = NewBook.query.filter_by(isbn=isbn).all()
            for book in books_to_delete:
                db.session.delete(book)
                print("deleted Books")
            for book in new_books_to_delete:
                db.session.delete(book)
                print("deleted newBooks")

        db.session.commit()
