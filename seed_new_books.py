import csv

from app import db

from app.models.books import Book

from app.models.new_books import NewCategory, NewCategoryBook, NewBook

print(db)

def seed_new_books():
    print("Processing")

    ############################# Books

    books = []
    with open("./must-read-books.csv", mode="r", encoding='utf8') as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            books.append(line)

    books = books[1:]

    for i in range(len(books)): 
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
        book = books[i]

        added_book = Book.query.filter_by(isbn=book[5]).first()
        if not added_book: 
            try: 
                Book.create(
                     book[7],
                     book[6],
                     book[5],
                     book[8],
                     book[9],
                     '',
                     'English',
                     '',
                     '',
                     1,
                     None,
                     None,
                     None,
                     None
                )
                print(f'Added Book - {book[7]}')
                added_book = Book.query.filter_by(isbn=book[5]).first()
                min_age, max_age = int(book[0]), int(book[1])
                if (min_age >= 0 and min_age <= 2) or (max_age >= 0 and max_age <= 2): 
                    added_book.age_group_1 = True
                if (min_age >= 3 and min_age <= 5) or (max_age >= 3 and max_age <= 5): 
                    added_book.age_group_1 = True
                if (min_age >= 6 and min_age <= 8) or (max_age >= 6 and max_age <= 8): 
                    added_book.age_group_1 = True
                if (min_age >= 9 and min_age <= 11) or (max_age >= 9 and max_age <= 11): 
                    added_book.age_group_1 = True
                if (min_age >= 12 and min_age <= 14) or (max_age >= 12 and max_age <= 14): 
                    added_book.age_group_1 = True
                if (min_age >= 15) or (max_age >= 15): 
                    added_book.age_group_1 = True
                db.session.commit()
            except Exception as e: 
                print(e)
                continue
        else: 
            print(f'Already added {book[7]}')

        # added_book = NewBook.query.filter_by(isbn=book[5]).first()
        # if not added_book: 
        #     try: 
        #         NewBook.create(
        #             book[7],
        #             book[6],
        #             book[5],
        #             book[8],
        #             book[9].replace(',', ''),
        #             book[4],
        #             book[0],
        #             book[1],
        #         )
        #         added_book = NewBook.query.filter_by(isbn=book[5]).first()
        #         print(f'Added book - {book[2]} - {i + 1}/{len(books)}')
        #     except Exception as e: 
        #         print(e)
        #         continue
        # else: 
        #     print(f'Already added book - {book[2]} - {i + 1}/{len(books)}')
        # category = NewCategory.query.filter_by(name=book[3]).first()
        # if not category: 
        #     NewCategory.create(
        #         book[3],
        #         book[2],
        #         book[0],
        #         book[1]
        #     )
        #     category = NewCategory.query.filter_by(name=book[3]).first()
        # category.min_age = min(category.min_age, int(book[0]))
        # category.max_age = max(category.max_age, int(book[1]))
        # db.session.commit()
        # NewCategoryBook.create(
        #     category.id,
        #     added_book.id
        # )