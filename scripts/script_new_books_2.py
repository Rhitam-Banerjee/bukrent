import csv

from app import db

from app.models.new_books import NewBookImage, NewBook, NewCategoryBook, NewBookImage, NewCategory
from app.models.books import Book

from datetime import datetime

def seed_new_books():
    print("Processing")

    ############################# Books

    books = []
    with open("./scripts/data/new_books.csv", mode="r", encoding='utf8') as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            books.append(line)

    books = books[1:]
    new_book_ids = set()
    new_category_ids = set()

    for i in range(len(books)): 
        '''
        0 - isbn
        1 - category_name
        2 - max_age
        3 - min_age
        4 - book_name
        5 - rating
        6 - review_count
        7 - main_image
        8 - category_other_name
        '''
        book = books[i]
        book = {
            'isbn': books[i][0],
            'category_name': books[i][1],
            'min_age': books[i][3],
            'max_age': books[i][2],
            'book_name': books[i][4],
            'rating': books[i][5],
            'review_count': books[i][6],
            'main_image': books[i][7],
            'category_other_name': books[i][8],
        }

        ''' Adding to the new books table '''

        added_book = NewBook.query.filter_by(isbn=book['isbn']).first()
        if added_book: 
            for category in added_book.categories: 
                category_book = NewCategoryBook.query.filter_by(category_id=category.id, book_id=added_book.id).first()
                category_book.delete()
            book_images = NewBookImage.query.filter_by(book_id=added_book.id).all()
            for book_image in book_images: 
                book_image.delete()

            added_book.name = book['book_name']
            added_book.image = book['main_image']
            added_book.rating = book['rating']
            added_book.review_count = book['review_count']
            added_book.min_age = book['min_age']
            added_book.max_age = book['max_age']

            db.session.commit()
            print(f'Updated book: {added_book.name} - {i + 1} / {len(books)}')
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
            print(f'Added book: {i + 1} / {len(books)}')

        added_book = NewBook.query.filter_by(isbn=book['isbn']).first()

        category_name, category_other_name = book['category_name'], book['category_other_name']
        category, category_other = None, None
        if category_name: 
            category = NewCategory.query.filter(NewCategory.name.ilike(f'{category_name}%')).first()
            if not category: 
                NewCategory.create(category_name, 10000, book['min_age'], book['max_age'])
                category = NewCategory.query.filter(NewCategory.name.ilike(f'{category_name}%')).first()
        if category_other_name: 
            category_other = NewCategory.query.filter(NewCategory.name.ilike(f'{category_other_name}%')).first()
            if not category_other: 
                NewCategory.create(category_other_name, 0, book['min_age'], book['max_age'])
                category_other = NewCategory.query.filter(NewCategory.name.ilike(f'{category_other_name}%')).first()

        new_book_ids.add(added_book.id)
        if category: 
            NewCategoryBook.create(category.id, added_book.id, 1)
            new_category_ids.add(category.id)
        if category_other: 
            NewCategoryBook.create(category_other.id, added_book.id, 1)        
            new_category_ids.add(category_other.id)

        ''' X '''

        ''' Adding to the old books table '''

        old_book = Book.query.filter_by(isbn=book['isbn']).first()
        if old_book: 
            old_book.name = book['book_name']
            old_book.image = book['main_image']
            old_book.rating = book['rating']
            old_book.review_count = book['review_count']
            print(f'Updated old book: {added_book.name} - {i + 1} / {len(books)}')
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

    all_new_books = NewBook.query.all()
    for new_book in all_new_books: 
        if new_book.id not in new_book_ids: 
            print(f'Deleting book - {new_book.name}')
            for category in new_book.categories: 
                category_book = NewCategoryBook.query.filter_by(category_id=category.id, book_id=new_book.id).first()
                category_book.delete()
            book_images = NewBookImage.query.filter_by(book_id=new_book.id).all()
            for book_image in book_images: 
                book_image.delete()
            new_book.delete()

    all_new_categories = NewCategory.query.all()
    for new_category in all_new_categories: 
        if new_category.id not in new_category_ids: 
            print(f'Deleting category - {new_category.name}')
            category_books = NewCategoryBook.query.filter_by(category_id=new_category.id).all()
            for category_book in category_books: 
                category_book.delete()
            new_category.delete()

    db.session.commit()