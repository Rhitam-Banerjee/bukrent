import csv

from app import db

from app.models.new_books import NewBookImage, NewBook

from datetime import datetime

def seed_new_books():
    print("Processing")

    ############################# Books

    books = []
    with open("./scripts/data/new_books_details.csv", mode="r", encoding='utf8') as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            books.append(line)

    books = books[1:]

    for i in range(len(books)): 
        '''
        0 - name
        1 - rating
        2 - review_count
        3 - price
        4 - for_age
        5 - grade_level
        6 - lexile_measure
        7 - pages
        8 - language
        9 - dimensions
        10 - publisher
        11 - isbn
        12 - main_image
        13 - sub_image
        14 - sub_image
        15 - sub_image
        '''
        book = books[i]

        isbn = book[11]
        images = book[13:]

        added_book = NewBook.query.filter_by(isbn=isbn).first()
        if added_book:
            for image in images: 
                if image: 
                    NewBookImage.create(image, added_book.id)

            db.session.commit()

            print(f'{i + 1} / {len(books)}')
        else: 
            print(f'Skipped book: {i + 1}')            