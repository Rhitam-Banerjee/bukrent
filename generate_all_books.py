from app import create_app, db
from app.models.new_books import NewBook, NewCategory, NewCategoryBook, NewBookSection
from app.models.buckets import Dump, Wishlist
from app.models.books import Book
from app.models.order import Order
import xlsxwriter

app = create_app()
db.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/bukrent'

with app.app_context():
    iterator = 0
    books = NewBook.query.all()
    workbook = xlsxwriter.Workbook("/home/linuxuser/Downloads/All_books.xlsx")
    worksheet = workbook.add_worksheet("All")
    worksheet.write(iterator, 0, "ISBN")
    worksheet.write(iterator, 1, "Name")
    worksheet.write(iterator, 2, "Author_1")
    worksheet.write(iterator, 3, "Author_2")
    worksheet.write(iterator, 4, "Author_3")
    worksheet.write(iterator, 5, "Browser Library")
    worksheet.write(iterator, 6, "Best Seller Series")
    worksheet.write(iterator, 7, "Most Searched Tag")
    worksheet.write(iterator, 8, "Most Popular Series")
    worksheet.write(iterator, 9, "Review_Count")
    worksheet.write(iterator, 10, "Price")
    worksheet.write(iterator, 11, "Min_Age")
    worksheet.write(iterator, 12, "Max_Age")
    worksheet.write(iterator, 13, "Image Link")

    for book in books:
        iterator += 1
        old_book = Book.query.filter_by(isbn=book.isbn).first()
        '''wishlist_count = Wishlist.query.filter_by(book_id=old_book.id).count()
        previous_count = Dump.query.filter_by(book_id=old_book.id, read_before=True).count() + \
                         Order.query.filter_by(book_id=old_book.id).count()
        available = old_book.stock_available
        rentals = old_book.rentals'''
        new_category_book = NewCategoryBook.query.filter_by(book_id=book.id).all()
        if new_category_book:
            for category_book in new_category_book:
                category = NewCategory.query.filter_by(id=category_book.category_id).all()
                section_id = category_book.section_id
                if section_id == 1:
                    worksheet.write(iterator, 5, "".join([x.name for x in category]))
                elif section_id == 3:
                    worksheet.write(iterator, 8, "".join([x.name for x in category]))
                elif section_id == 4:
                    worksheet.write(iterator, 6, "".join([x.name for x in category]))
                elif section_id == 5:
                    worksheet.write(iterator, 7, "".join([x.name for x in category]))
        worksheet.write(iterator, 0, book.isbn)
        worksheet.write(iterator, 1, book.name)
        worksheet.write(iterator, 9, book.review_count)
        worksheet.write(iterator, 10, book.price)
        worksheet.write(iterator, 11, book.min_age)
        worksheet.write(iterator, 12, book.max_age)
        worksheet.write(iterator, 13, book.image)
        if book.authors:
            authors = [x.strip() for x in book.authors.split(",") if x]
        else:
            authors = []
        start_author = 2
        for x in authors:
            worksheet.write(iterator, start_author, x)
            start_author += 1
    workbook.close()
