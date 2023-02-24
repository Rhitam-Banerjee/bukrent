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

        name = book[0]
        price = book[3]
        for_age = book[4]
        grade_level = book[5]
        lexile_measure = book[6]
        pages = book[7]
        language = book[8]
        dimensions = book[9]
        publisher = book[10]
        isbn = book[11]
        main_image = book[12]
        images = book[12:]

        added_book = NewBook.query.filter_by(isbn=isbn).first()
        if added_book: 
            if price: 
                added_book.price = price.replace(',', '')
            else: 
                added_book.price = None
            if for_age: 
                added_book.for_age = for_age
            else: 
                added_book.for_age = None
            if grade_level: 
                added_book.grade_level = grade_level
            else: 
                added_book.grade_level = None
            if lexile_measure: 
                added_book.lexile_measure = lexile_measure
            else: 
                added_book.lexile_measure = None
            if pages: 
                added_book.pages = pages.replace(',', '')
            else: 
                added_book.pages = None
            if language: 
                added_book.language = language
            else: 
                added_book.language = None
            if dimensions: 
                added_book.dimensions = dimensions
            else: 
                added_book.dimensions = None
            if publisher: 
                added_book.publisher = publisher
            else: 
                added_book.publisher = None
            # if main_image: 
            #     added_book.image = main_image
            # for image in images: 
            #     if image: 
            #         NewBookImage.create(image, added_book.id)

            db.session.commit()

            print(f'{i + 1} / {len(books)}')
        else: 
            print(f'Skipped book: {name}')            