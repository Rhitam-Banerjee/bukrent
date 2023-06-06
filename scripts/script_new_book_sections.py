import csv

from app import db
from app.models.new_books import NewBook, NewCategoryBook, NewCategory, NewBookSection
from app.models.books import Book

def seed_new_book_sections():
    print("Processing")

    ############################# Books

    books = []
    with open("./scripts/data/new_book_sections.csv", mode="r", encoding='utf8') as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            books.append(line)

    books = books[1:]

    most_popular_series = NewBookSection.query.filter_by(name='Most Popular Series').first()
    best_seller_series = NewBookSection.query.filter_by(name='Best Seller Series').first()
    most_searched_tags = NewBookSection.query.filter_by(name='Most Searched Tags').first()
    if not most_popular_series: 
        NewBookSection.create('Most Popular Series') 
        most_popular_series = NewBookSection.query.filter_by(name='Most Popular Series').first()
    if not best_seller_series: 
        NewBookSection.create('Best Seller Series') 
        best_seller_series = NewBookSection.query.filter_by(name='Best Seller Series').first()
    if not most_searched_tags: 
        NewBookSection.create('Most Searched Tags') 
        most_searched_tags = NewBookSection.query.filter_by(name='Most Searched Tags').first()

    most_popular_series_category = NewCategory.query.filter_by(name='Most Popular Series').first()
    if not most_popular_series_category: 
        NewCategory.create('Most Popular Series', 100, 0, 100)
        most_popular_series_category = NewCategory.query.filter_by(name='Most Popular Series').first()

    for i in range(len(books)): 
        '''
        0 - isbn
        1 - category_name
        2 - review_count
        3 - most_popular
        4 - best_seller
        5 - most_searched
        6 - book_name
        7 - min_age
        8 - max_age
        9 - rating
        '''
        book = books[i]
        book = {
            'isbn': books[i][0],
            'category_name': books[i][1],
            'most_popular': books[i][3],
            'best_seller': books[i][4],
            'most_searched': books[i][5],
            'min_age': books[i][7],
            'max_age': books[i][8],
        }

        ''' Adding new sections '''

        added_book = NewBook.query.filter_by(isbn=book['isbn']).first()
        if added_book: 
            if book['most_popular']: 
                NewCategoryBook.create(
                    most_popular_series_category.id, 
                    added_book.id, 
                    most_popular_series.id,
                )
                print(f'Added to most popular : {i + 1} / {len(books)}')
            if book['best_seller']: 
                category = NewCategory.query.filter_by(name=book['best_seller']).first()
                if not category: 
                    NewCategory.create(book['best_seller'], 100, book['min_age'], book['max_age'])
                    category = NewCategory.query.filter_by(name=book['best_seller']).first()
                NewCategoryBook.create(
                    category.id,
                    added_book.id,
                    best_seller_series.id,
                )
                print(f'Added to best seller : {i + 1} / {len(books)}')
            if book['most_searched']: 
                category = NewCategory.query.filter_by(name=book['most_searched']).first()
                if not category: 
                    NewCategory.create(book['most_searched'], 100, book['min_age'], book['max_age'])
                    category = NewCategory.query.filter_by(name=book['most_searched']).first()
                NewCategoryBook.create(
                    category.id,
                    added_book.id,
                    most_searched_tags.id,
                )
                print(f'Added to most searched tags : {i + 1} / {len(books)}')
        else: 
            print(f'Skipped : {i + 1} / {len(books)}')

        ''' X '''

    db.session.commit()
