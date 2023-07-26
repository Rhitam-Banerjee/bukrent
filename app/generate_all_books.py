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
    worksheet.write(iterator, 5, "Best Seller Series")
    worksheet.write(iterator, 6, "Most Searched Tag")
    worksheet.write(iterator, 7, "Most Popular Series")
    worksheet.write(iterator, 8, "Review_Count")
    worksheet.write(iterator, 9, "Price")
    worksheet.write(iterator, 10, "Min_Age")
    worksheet.write(iterator, 11, "Max_Age")
    worksheet.write(iterator, 12, "Image Link")

    for book in books:
        iterator += 1
        old_book = Book.query.filter_by(isbn=book.isbn).first()
        '''wishlist_count = Wishlist.query.filter_by(book_id=old_book.id).count()
        previous_count = Dump.query.filter_by(book_id=old_book.id, read_before=True).count() + \
                         Order.query.filter_by(book_id=old_book.id).count()
        available = old_book.stock_available
        rentals = old_book.rentals'''
        new_category = NewCategoryBook.query.filter_by(book_id=book.id).first()
        if new_category:
            category = NewCategory.query.filter_by(id=new_category.category_id).first()
            section_id = new_category.section_id
            if section_id == 4:
                worksheet.write(iterator, 5, category.name)
            elif section_id == 5:
                print("5 printer")
                worksheet.write(iterator, 6, category.name)
            elif section_id == 3:
                print("3 printed")
                worksheet.write(iterator, 3, category.name)
            section = NewBookSection.query.filter_by(id=section_id).first()

        worksheet.write(iterator, 0, book.isbn)
        worksheet.write(iterator, 1, book.name)
        worksheet.write(iterator, 8, book.review_count)
        worksheet.write(iterator, 9, book.price)
        worksheet.write(iterator, 10, book.min_age)
        worksheet.write(iterator, 11, book.max_age)
        worksheet.write(iterator, 12, book.image)
        if book.authors:
            authors = [x.strip() for x in book.authors.split(",") if x]
        else:
            authors = []
        start_author = 2
        for x in authors:
            worksheet.write(iterator, start_author, x)
            start_author += 1
    workbook.close()
