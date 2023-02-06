import csv

from app import db

from app.models.new_books import NewBook

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
        try: 
            book = books[i]
            if NewBook.query.filter_by(isbn=book[5]).count(): 
                print(f'Already added book - {book[2]} - {i + 1}/{len(books)}')
                continue
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
            NewBook.create(
                book[7],
                book[6],
                book[5],
                book[8],
                book[9].replace(',', ''),
                book[3],
                book[4],
                book[2],
                book[0],
                book[1],
            )

            print(f'Added book - {book[2]} - {i + 1}/{len(books)}')
        except: 
            continue