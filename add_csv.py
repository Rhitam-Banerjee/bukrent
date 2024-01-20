from app import create_app, db
from app.models.new_books import NewBook, Book, NewCategory, NewCategoryBook, NewBookSection, Book, NewBookImage
import openpyxl 
from sqlalchemy import update
import sys 

app = create_app()
db.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/bukrent'

with app.app_context():
    csv_file_path = 'Books.xlsx'
    books = []
    workbook = openpyxl.load_workbook(csv_file_path)
    sheet = workbook.active
    iterator = sheet.iter_rows()
    header_row = next(iterator)
    header_row = {i: header_row[i].value.lower() for i in range(len(header_row))}
    for row in iterator:
        temp = {}
        for i in header_row:
            string_values = {"name", "genres", "category", "size", "author 1", "publication", "author 2", "author 3", "author 4", "book description", "image", "side image 1", "side image 2", "side image 3", "side image 4"}
            integer_values = {"rating", "review_count", "min_age", "max_age", "isbn"}
            pages = {"pages"}
            if header_row[i] in string_values:
                temp[header_row[i]] = ""
            elif header_row[i] in integer_values:
                temp[header_row[i]] = 0
            elif header_row[i] in pages:
                temp[header_row[i]] = "0 pages"
        for cell in range(len(row)):
            if row[cell].value != None:
                if isinstance(row[cell].value, float):
                    row[cell].value = int(row[cell].value)
                temp[header_row[cell]] = row[cell].value
        if temp:
            # Existing books logic
            try:
                split = temp['image'].split(".")
                split[-2] = split[-2].replace('600', '218')
                temp['image'] = ".".join(split)
            except: 
                print(temp)
                pass
            isbn = str(temp['isbn'])
            fetch_book = NewBook.query.filter_by(isbn=isbn).first()
            if fetch_book:
                update_new_book = update(NewBook).where(NewBook.isbn == isbn).values(name=temp['name'], image=temp['image'], isbn = temp['isbn'], rating=temp['rating'], review_count=temp['review_count'], min_age=temp['min_age'], max_age=temp['max_age'], pages=int(temp['pages'].split(" ")[0]), dimensions=temp['size'], publisher=temp['publication'], authors=",".join([x for x in [temp['author 1'], temp['author 2'], temp['author 3'], temp['author 4']] if x]), description=temp['book description']).returning(NewBook.id)
                updated_id = db.engine.execute(update_new_book).fetchone()
                update_book = update(Book).where(Book.isbn == isbn).values(name=temp['name'], image=temp['image'], isbn=temp['isbn'], rating=temp['rating'], review_count=temp['review_count'], description=temp['book description'])
                db.engine.execute(update_book)
                print("UPDATED", isbn)
            

            # New books that were to be added 
            # temp['isbn'] = str(temp['isbn'])
            # books.append(temp['isbn'])
            # Book.create(temp['name'], temp['image'], temp['isbn'], temp['rating'], temp['review_count'], "", "", None, temp['book description'], 0, None, None, None, None)
            # new_book_instance = NewBook.create(temp['name'], temp['image'], temp['isbn'], temp['rating'], temp['review_count'], temp['min_age'], temp['max_age'],None, None, temp['genres'], int(temp['pages'].split(" ")[0]), None, temp['book description'], temp['publication'], None, None, None, None, ",".join([x for x in [temp['author 1'], temp['author 2'], temp['author 3'], temp['author 4']] if x]))
            # category_id = NewCategory.create(temp['category'], 0, temp['min_age'], temp['max_age'])
            # NewCategoryBook.create(category_id, new_book_instance, 1)
            # for side_image in [temp['side image 1'], temp['side image 2'], temp['side image 3'], temp['side image 4']]:
            #     if side_image:
            #         NewBookImage.create(side_image, new_book_instance, 0)
            

