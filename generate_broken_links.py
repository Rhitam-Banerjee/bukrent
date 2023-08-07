from app import create_app, db
from urllib.parse import urlparse
import xlsxwriter
from app.models.user import User

app = create_app()
db.init_app(app)

with app.app_context():
    users = User.query.all()
    workbook = xlsxwriter.Workbook("/home/ubuntu/bukrent/books_with_broken_links_in_wishlist.xlsx")
    worksheet = workbook.add_worksheet("All")
    for x in users:
        if x.wishlist:
            books = [x for x in x.wishlist if urlparse(x.book.image).netloc and urlparse(x.book.image).netloc[0] == "d"]
            iterator = 0
            worksheet.write(iterator, 0, "ISBN")
            worksheet.write(iterator, 1, "Name")
            worksheet.write(iterator, 2, "Image Link")
            for book in books:
                iterator += 1
                worksheet.write(iterator, 0, book.book.isbn)
                worksheet.write(iterator, 1, book.book.name)
                worksheet.write(iterator, 2, book.book.image)
    workbook.close()
