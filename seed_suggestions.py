from app import create_app, db
from app.models.new_books import NewBook, NewCategory, NewCategoryBook
from app.models.buckets import Dump, Wishlist
from app.models.books import Book
from app.models.order import Order
import xlsxwriter

app = create_app()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/bukrent'

with app.app_context():
    iterator = 0
    books = NewBook.query.all()
    workbook = xlsxwriter.Workbook("./All_books.xlsx")
    worksheet = workbook.add_worksheet("All")
    worksheet.write(iterator, 0, "ISBN")
    worksheet.write(iterator, 1, "Name")
    worksheet.write(iterator, 2, "Review_Count")
    worksheet.write(iterator, 3, "Available")
    worksheet.write(iterator, 4, "Rentals")
    worksheet.write(iterator, 5, "Category")
    worksheet.write(iterator, 6, "Wishlist")
    worksheet.write(iterator, 7, "Previous")

    for book in books:
        iterator += 1
        old_book = Book.query.filter_by(isbn=book.isbn).first()
        if old_book is not None:
         wishlist_count = Wishlist.query.filter_by(book_id=old_book.id).count()
         previous_count = Dump.query.filter_by(book_id=old_book.id, read_before=True).count() + \
                         Order.query.filter_by(book_id=old_book.id).count()
         available = old_book.stock_available
         rentals = old_book.rentals
        category_id = NewCategoryBook.query.filter_by(book_id=book.id).first()
        if category_id:
            category = NewCategory.query.filter_by(id=category_id.category_id).first()
            worksheet.write(iterator, 5, category.name)
        worksheet.write(iterator, 0, book.isbn)
        worksheet.write(iterator, 1, book.name)
        worksheet.write(iterator, 2, book.review_count)
        worksheet.write(iterator, 3, available)
        worksheet.write(iterator, 4, rentals)
        worksheet.write(iterator, 6, wishlist_count)
        worksheet.write(iterator, 7, previous_count)
    workbook.close()
