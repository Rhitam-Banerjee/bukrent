import csv

from app import db

from app.models.new_books import NewCategory, NewCategoryBook, NewBook

print(db)

def seed_new_books():
    print("Processing")

    ############################# Books

    books = []
    with open("./new_books_data.csv", mode="r", encoding='utf8') as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            books.append(line)

    books = books[1:]

    for i in range(len(books)): 
        book = books[i]
        added_book = NewBook.query.filter_by(isbn=book[5]).first()
        if not added_book: 
            try: 
                NewBook.create(
                    book[7],
                    book[6],
                    book[5],
                    book[8],
                    book[9].replace(',', ''),
                    book[4],
                    book[0],
                    book[1],
                )
                added_book = NewBook.query.filter_by(isbn=book[5]).first()
                print(f'Added book - {book[2]} - {i + 1}/{len(books)}')
            except Exception as e: 
                print(e)
                continue
        else: 
            print(f'Already added book - {book[2]} - {i + 1}/{len(books)}')
        category = NewCategory.query.filter_by(name=book[3]).first()
        if not category: 
            NewCategory.create(
                book[3],
                book[2],
                book[0],
                book[1]
            )
            category = NewCategory.query.filter_by(name=book[3]).first()
        category.min_age = min(category.min_age, int(book[0]))
        category.max_age = max(category.max_age, int(book[1]))
        db.session.commit()
        NewCategoryBook.create(
            category.id,
            added_book.id
        )
        '''
        0 - min_age
        1 - max_age
        2 - category_order
        3 - category
        4 - book_order
        5 - isbn
        6 - image
        7 - name
        8 - rating
        9 - review_count
        '''