from app.models.user import *
from app.models.buckets import *
from app.models.order import *
from app.models.books import Book

from sqlalchemy import and_

import csv

def sept_8():
    suggestions_data = []
    with open("scripts/data/8_sept/isbn.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            suggestions_data.append(line)

    suggestions_data = suggestions_data[1:]

    user_suggestion_dict = {}
    for mobile_number in suggestions_data[0]:
        user_suggestion_dict[mobile_number] = []

    for mobile_number, empty_list in user_suggestion_dict.items():
        column = suggestions_data[0].index(mobile_number)
        row = 0
        while row <= int(suggestions_data[1][column]):
            if suggestions_data[row+2][column]:
                empty_list.append(suggestions_data[row+2][column])
            row += 1
        print(f"Column {column} done!")

    total_suggestions = 0
    for mobile_number, isbn_list in user_suggestion_dict.items():
        user_obj = User.query.filter_by(mobile_number=mobile_number).first()
        if user_obj:
            suggestions = user_obj.suggestions
            for suggestion in suggestions:
                suggestion.delete()
            
            for isbn in isbn_list:
                book = Book.query.filter_by(isbn=isbn).first()
                if not book:
                    isbn_list.remove(isbn)
                else:
                    wishlist_obj = Wishlist.query.filter(and_(Wishlist.user_id==user_obj.id, Wishlist.book_id==book.id)).first()
                    if not wishlist_obj:
                        dump_obj = Dump.query.filter(and_(Dump.user_id==user_obj.id, Dump.book_id==book.id)).first()
                        if not dump_obj:
                            age_group = None
                            if book.suggestion_age1:
                                age_group = 1
                            elif book.suggestion_age2:
                                age_group = 2
                            elif book.suggestion_age3:
                                age_group = 3
                            elif book.suggestion_age4:
                                age_group = 4
                            elif book.suggestion_age5:
                                age_group = 5
                            elif book.suggestion_age6:
                                age_group = 6
                            if not age_group:
                                if book.bestseller_age1:
                                    age_group = 1
                                elif book.bestseller_age2:
                                    age_group = 2
                                elif book.bestseller_age3:
                                    age_group = 3
                                elif book.bestseller_age4:
                                    age_group = 4
                                elif book.bestseller_age5:
                                    age_group = 5
                                elif book.bestseller_age6:
                                    age_group = 6
                                if not age_group:
                                    book.suggestion_age3 = True
                                    db.session.add(book)
                                    db.session.commit()

                                    age_group = 3

                            Suggestion.create(user_obj.id, book.id, age_group)
            print(f"{mobile_number} has {len(isbn_list)} books")
            total_suggestions += len(isbn_list)

    print(f"Total suggestions - {total_suggestions}")
    print(f"Suggestions Created - {len(Suggestion.query.all())}")