import csv

from app import db

from app.models.books import Book

def seed_books():
    print("Processing")

    ############################# Books

    books = []
    with open("./books.csv", mode="r", encoding='utf8') as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            books.append(line)

    books = books[1:]

    for i in range(len(books)): 
        book = books[i]
        if Book.query.filter_by(isbn=book[4]).count(): 
            print(f'Already added book - {book[2]} - {i + 1}/{len(books)}')
            continue
        Book.create(
            book[2],
            book[3],
            book[4],
            book[5],
            book[6],
            book[7],
            book[8],
            book[9],
            book[10],
            book[11],
            None,
            None,
            None,
            {
                "suggestion_age1": bool(book[26]),
                "suggestion_age2": bool(book[27]),
                "suggestion_age3": bool(book[28]),
                "suggestion_age4": bool(book[29]),
                "suggestion_age5": bool(book[30]),
                "suggestion_age6": bool(book[31]),
            },
        )

        book_obj = Book.query.filter_by(isbn=book[4]).first()

        book_obj.amazon_bestseller = bool(book[12])
        book_obj.bestseller_age1 = bool(book[13])
        book_obj.bestseller_age2 = bool(book[14])
        book_obj.bestseller_age3 = bool(book[15])
        book_obj.bestseller_age4 = bool(book[16])
        book_obj.bestseller_age5 = bool(book[17])
        book_obj.bestseller_age6 = bool(book[18])

        book_obj.most_borrowed = bool(book[19])
        book_obj.borrowed_age1 = bool(book[20])
        book_obj.borrowed_age2 = bool(book[21])
        book_obj.borrowed_age3 = bool(book[22])
        book_obj.borrowed_age4 = bool(book[23])
        book_obj.borrowed_age5 = bool(book[24])
        book_obj.borrowed_age6 = bool(book[25])

        book_obj.age_group_1 = bool(book[34])
        book_obj.age_group_2 = bool(book[35])
        book_obj.age_group_3 = bool(book[36])
        book_obj.age_group_4 = bool(book[37])
        book_obj.age_group_5 = bool(book[38])
        book_obj.age_group_6 = bool(book[39])

        print(f'Added book - {book[2]} - {i + 1}/{len(books)}')