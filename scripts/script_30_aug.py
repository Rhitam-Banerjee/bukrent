from app.models.user import *
from app.models.books import Book
from app.models.order import Order

import csv

from app import db

import datetime

from sqlalchemy import and_

def aug_30_1():
    all_users = User.query.all()

    for user in all_users:
        if len(user.child) > 0:
            if len(user.suggestions) == 0:
                age_groups = []
                for child in user.child:
                    age_groups.append(child.age_group)

                age_groups = list(set(age_groups))
                user.add_age_groups(age_groups)

    suggestions_data = []
    with open("scripts/data/30_aug/isbn.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            suggestions_data.append(line)

    suggestions_data = suggestions_data[1:]

    user_suggestion_dict = {}
    for mobile_number in suggestions_data[0]:
        user_suggestion_dict[mobile_number] = []

    for mobile_number, empty_list in user_suggestion_dict.items():
        user_obj = User.query.filter_by(mobile_number=mobile_number).first()
        column = suggestions_data[0].index(mobile_number)
        row = 0
        while row < int(suggestions_data[1][column]):
            if suggestions_data[row+2][column]:
                empty_list.append(suggestions_data[row+2][column])
                row += 1
    
    for mobile_number, isbn_list in user_suggestion_dict.items():
        user_obj = User.query.filter_by(mobile_number=mobile_number).first()
        for isbn in isbn_list:
            book = Book.query.filter_by(isbn=isbn).first()
            if not book:
                isbn_list.remove(isbn)
            else:
                ### Check if book is already there in Dump, Wishlist or Suggestion
                already_added = False
                suggestion = Suggestion.query.filter(and_(Suggestion.user_id==user_obj.id, Suggestion.book_id==book.id)).first()
                wishlist = Wishlist.query.filter(and_(Wishlist.user_id==user_obj.id, Wishlist.book_id==book.id)).first()
                dump = Dump.query.filter(and_(Dump.user_id==user_obj.id, Dump.book_id==book.id)).first()
                if not all((suggestion, wishlist, dump)):
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