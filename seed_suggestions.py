from app import create_app, db
from app.models.new_books import NewBook
from app.models.buckets import Dump, Wishlist
from app.models.books import Book
from app.models.order import Order
import xlsxwriter

app = create_app()
db.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'

with app.app_context():
    iterator = 0
    books = NewBook.query.all()
    workbook = xlsxwriter.Workbook("/home/linuxuser/All_books.xlsx")
    worksheet = workbook.add_worksheet("All")
    worksheet.write(iterator, 0, "ISBN")
    worksheet.write(iterator, 1, "Name")
    worksheet.write(iterator, 2, "Review_Count")
    worksheet.write(iterator, 3, "Available")
    worksheet.write(iterator, 4, "Rented")
    worksheet.write(iterator, 5, "Wishlist")
    worksheet.write(iterator, 6, "Previous")
    for book in books:
        iterator += 1
        old_book = Book.query.filter_by(isbn=book.isbn).first()
        wishlist_count = Wishlist.query.filter_by(book_id=old_book.id).count()
        previous_count = Dump.query.filter_by(book_id=old_book.id, read_before=True).count() + \
                         Order.query.filter_by(book_id=old_book.id).count()
        available = old_book.stock_available
        rentals = old_book.rentals
        worksheet.write(iterator, 0, book.isbn)
        worksheet.write(iterator, 1, book.name)
        worksheet.write(iterator, 2, book.review_count)
        worksheet.write(iterator, 3, available)
        worksheet.write(iterator, 4, rentals)
        worksheet.write(iterator, 5, wishlist_count)
        worksheet.write(iterator, 6, previous_count)
    workbook.close()





