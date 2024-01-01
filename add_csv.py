from app import create_app, db
from app.models.new_books import NewBook, Book, NewCategory, NewCategoryBook, NewBookSection, Book
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
            book_id = NewBook.create(row[1], row[2], row[0], row[3], row[4], row[5], row[6], row[7], "", None, "",row[13], "", None, None, None, None, row[12])
            Book.create(row[1], row[2], row[0], row[3], row[4], row[11], row[7], row[9], row[13], 0, None, None, None, None)
            category_id = NewCategory.create(row[8], 0, row[5], row[6])
            NewCategoryBook.create(category_id, book_id, 1)
            print("ADDED", book_id, category_id)