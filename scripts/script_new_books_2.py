import csv

from app import db
from app.models.new_books import NewBook, NewCategoryBook, NewCategory
from app.models.books import Book

def seed_new_books():
    print("Processing")

    ############################# Books

    books = []
    with open("./scripts/data/new_books_main_3_june.csv", mode="r", encoding='utf8') as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            books.append(line)

    books = books[1:]

    for i in range(len(books)): 
        '''
        0 - isbn
        1 - category_name
        2 - book_name
        3 - min_age
        4 - max_age
        5 - review_count
        6 - rating
        7 - main_image
        '''
        book = books[i]
        book = {
            'isbn': books[i][0],
            'category_name': books[i][1],
            'book_name': books[i][2],
            'min_age': books[i][3],
            'max_age': books[i][4],
            'review_count': books[i][5],
            'rating': books[i][6],
            'main_image': books[i][7],
        }

        ''' Adding to the new books table '''

        added_book = NewBook.query.filter_by(isbn=book['isbn']).first()
        if added_book: 
            pass
            # for category in added_book.categories: 
            #     category_book = NewCategoryBook.query.filter_by(category_id=category.id, book_id=added_book.id).first()
            #     category_book.delete()
            # book_images = NewBookImage.query.filter_by(book_id=added_book.id).all()
            # for book_image in book_images: 
            #     book_image.delete()

            # added_book.name = book['book_name']
            # added_book.image = book['main_image']
            # added_book.rating = book['rating']
            added_book.review_count = int(book['review_count'].replace(',', ''))
            # added_book.min_age = book['min_age']
            # added_book.max_age = book['max_age']

            # db.session.commit()
            print(f'Skipped book: {added_book.name} - {i + 1} / {len(books)}')
        else: 
            NewBook.create(
                book['book_name'], 
                book['main_image'], 
                book['isbn'], 
                book['rating'], 
                book['review_count'], 
                1, 
                book['min_age'], 
                book['max_age']
            )

            added_book = NewBook.query.filter_by(isbn=book['isbn']).first()

            category_name = book['category_name']
            category = None
            if category_name: 
                category = NewCategory.query.filter(NewCategory.name.ilike(f'{category_name}%')).first()
                if not category: 
                    NewCategory.create(category_name, 10000, book['min_age'], book['max_age'])
                    category = NewCategory.query.filter(NewCategory.name.ilike(f'{category_name}%')).first()
            if category: 
                NewCategoryBook.create(category.id, added_book.id, 1)

            print(f'Added book: {i + 1} / {len(books)}')

        ''' X '''

        ''' Adding to the old books table '''

        old_book = Book.query.filter_by(isbn=book['isbn']).first()
        if old_book: 
            # old_book.name = book['book_name']
            # old_book.image = book['main_image']
            # old_book.rating = book['rating']
            old_book.review_count = int(book['review_count'].replace(',', ''))
            print(f'Skipped old book: {added_book.name} - {i + 1} / {len(books)}')
        else: 
            Book.create(
                book['book_name'], 
                book['main_image'], 
                book['isbn'], 
                book['rating'],
                book['review_count'], 
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
            print(f'Added old book: {i + 1} / {len(books)}')

        ''' X '''

    triple_zero_books = NewBook.query.filter(NewBook.isbn.ilike('000%')).all()
    print(f'{len(triple_zero_books)} triple zero books')
    for i in range(len(triple_zero_books)): 
        triple_zero_books[i].delete()
        print(f'Deleted {i + 1} / {len(triple_zero_books)}')
    triple_zero_books = Book.query.filter(Book.isbn.ilike('000%')).all()
    print(f'{len(triple_zero_books)} triple zero books')
    for i in range(len(triple_zero_books)): 
        triple_zero_books[i].delete()
        print(f'Deleted {i + 1} / {len(triple_zero_books)}')
    db.session.commit()
    db.session.commit()

    db.session.commit()
