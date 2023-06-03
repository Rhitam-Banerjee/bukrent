import csv

from app import db
from app.models.new_books import NewBook
from app.models.books import Book

def seed_new_books_description():
    print("Processing")

    ############################# Books

    books = []
    with open("./scripts/data/new_books_description_3_june.csv", mode="r", encoding='utf8') as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            books.append(line)

    books = books[1:]

    for i in range(len(books)): 
        '''
        0 - isbn
        1 - series
        2 - description
        '''
        book = books[i]
        book = {
            'isbn': books[i][0],
            'series': books[i][1],
            'description': books[i][2],
        }

        ''' Adding book description '''

        added_book = NewBook.query.filter_by(isbn=book['isbn']).first()
        if added_book: 
            added_book.description = book['description']

            db.session.commit()

            print(f'Added book description: {added_book.name} - {i + 1} / {len(books)}')
        else: 
            print(f'Skipped book description: {i + 1} / {len(books)}')

        ''' X '''

        ''' Adding description to the old books table '''

        old_book = Book.query.filter_by(isbn=book['isbn']).first()
        if old_book: 
            old_book.description = book['description']

            db.session.commit()

            print(f'Added old book description: {old_book.name} - {i + 1} / {len(books)}')
        else: 
            print(f'Skipped old book description: {i + 1} / {len(books)}')

        ''' X '''

    db.session.commit()