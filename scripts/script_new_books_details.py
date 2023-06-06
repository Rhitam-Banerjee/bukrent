import csv
from datetime import datetime

from app import db
from app.models.new_books import NewBook, NewBookImage
from app.models.books import Book

def seed_new_books_details():
    print("Processing")

    ############################# Books

    books = []
    with open("./scripts/data/new_books_main_6_june.csv", mode="r", encoding='utf8') as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            books.append(line)

    books = books[1:]

    for i in range(len(books)): 
        '''
        0 - isbn
        1 - series
        2 - name
        3 - rating
        4 - review
        5 - book_type
        6 - for_age
        7 - grade_level
        8 - lexile_measure
        9 - pages
        10 - language
        11 - dimensions
        12 - publisher
        13 - publication_date
        14 - isbn10
        15 - isbn13
        16 - author_1
        17 - author_2
        18 - author_3
        19 - main_image
        20 - image_1
        21 - image_2
        '''
        book = books[i]
        book = {
            'isbn': books[i][0],
            'name': books[i][2],
            'rating': books[i][3],
            'review_count': books[i][4],
            'book_type': books[i][5],
            'for_age': books[i][6],
            'grade_level': books[i][7],
            'lexile_measure': books[i][8],
            'pages': books[i][9],
            'language': books[i][10],
            'dimensions': books[i][11],
            'publisher': books[i][12],
            'publication_date': books[i][13],
            'isbn10': books[i][14],
            'isbn13': books[i][15],
            'author_1': books[i][16],
            'author_2': books[i][17],
            'author_3': books[i][18],
            'main_image': books[i][19],
            'image_1': books[i][20],
            'image_2': books[i][21],
        }

        for key in book: 
            if book[key].strip().lower() == 'not known': 
                book[key] = ''
            else: 
                book[key] = book[key].strip()

        ''' Adding book '''

        added_book = NewBook.query.filter_by(isbn=book['isbn']).first()
        if added_book: 
            print(f'Skipped book : {i + 1} / {len(books)}')
        else: 
            NewBook.create(
                book['name'], 
                book['main_image'], 
                book['isbn'], 
                book['rating'], 
                int(str(book['review_count']).replace(',', '')), 
                1, 
                book['min_age'], 
                book['max_age'],
            )

            added_book = NewBook.query.filter_by(isbn=book['isbn']).first()

            if book['book_type']: 
                added_book.book_type = book['book_type']
            if book['for_age']: 
                added_book.for_age = book['for_age']
            if book['grade_level']: 
                added_book.grade_level = book['grade_level']
            if book['lexile_measure']: 
                added_book.lexile_measure = book['lexile_measure']
            if book['pages']: 
                added_book.pages = book['pages']
            if book['language']: 
                added_book.language = book['language']
            if book['dimensions']: 
                added_book.dimensions = book['dimensions']
            if book['publisher']: 
                added_book.publisher = book['publisher']
            if book['publication_date']: 
                added_book.publication_date = datetime.strptime(book['publication_date'], '%B %d, %Y')
            if book['isbn10']: 
                added_book.isbn10 = book['isbn10']
            if book['isbn13']: 
                added_book.isbn13 = book['isbn13']
            
            authors = ''
            if book['author_1']: 
                authors += book['author_1'] + ', '
            if book['author_2']: 
                authors += book['author_2'] + ', '
            if book['author_3']: 
                authors += book['author_3']
            authors = authors.strip(', ')

            if authors: 
                added_book.authors = authors

            added_images = NewBookImage.query.filter_by(book_id=added_book.id).all()
            for image in added_images: 
                image.delete()

            if book['image_1']: 
                NewBookImage.create(book['image_1'], added_book.id)
            if book['image_2']: 
                NewBookImage.create(book['image_2'], added_book.id)


            print(f'Added book : {i + 1} / {len(books)}')

        ''' X '''

        ''' Adding old book '''

        old_book = Book.query.filter_by(isbn=book['isbn']).first()
        if old_book: 
            print(f'Skipped old book : {i + 1} / {len(books)}')
        else: 
            Book.create(
                book['book_name'], 
                book['main_image'], 
                book['isbn'], 
                book['rating'],
                int(str(book['review_count']).replace(',', '')),
                '', 
                'English', 
                None, 
                '', 
                1, 
                None, 
                None, 
                None, 
                None
            )
        
        ''' X '''

    db.session.commit()