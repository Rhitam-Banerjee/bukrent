from app.models.buckets import *
from app.models.user import *
from app.models.books import Book
from app.models.order import Order

import csv

from app import db

import datetime

from sqlalchemy import and_

def create_orders():
    orders = []
    with open("order_data.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            orders.append(line)

    orders = orders[1:]

    for order in orders:
        mobile_number = order[0]
        day = order[2]
        if order[3]:
            last_books = order[3].strip('][').replace("'", "").split(", ")
        else:
            last_books = []
        if order[4]:
            next_books = order[4].strip('][').replace("'", "").split(", ")
        else:
            next_books = []

        if day == "sat":
            last_day = datetime.datetime.strptime("20-08-2022", "%d-%m-%Y")
            next_day = datetime.datetime.strptime("27-08-2022", "%d-%m-%Y")
        if day == "wed":
            last_day = datetime.datetime.strptime("17-08-2022", "%d-%m-%Y")
            next_day = datetime.datetime.strptime("24-08-2022", "%d-%m-%Y")

        user = User.query.filter_by(mobile_number=mobile_number).first()
        if user:

            user.last_delivery_date = last_day
            user.next_delivery_date = next_day
            user.current_order = True
            if len(next_books) > 0:
                user.next_order_confirmed = True

            db.session.add(user)
            db.session.commit()

            for isbn in last_books:
                book = Book.query.filter_by(isbn=isbn).first()
                if book:
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
                    else:
                        age_group = 1

                    Order.create(user.id, book.id, age_group, last_day)

                    book.stock_available = book.stock_available - 1
                    db.session.add(book)
                    db.session.commit()

                    DeliveryBucket.create(user.id, book.id, last_day, age_group)

                    suggestion = Suggestion.query.filter(and_(Suggestion.user_id==user.id, Suggestion.book_id==book.id)).first()
                    if suggestion:
                        suggestion.delete()

            for isbn in next_books:
                book = Book.query.filter_by(isbn=isbn).first()
                if book:
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
                    else:
                        age_group = 1

                    book.stock_available = book.stock_available - 1
                    db.session.add(book)
                    db.session.commit()

                    DeliveryBucket.create(user.id, book.id, next_day, age_group)

                    user.next_order_confirmed = True
                    db.session.add(user)
                    db.session.commit()

                    suggestion = Suggestion.query.filter(and_(Suggestion.user_id==user.id, Suggestion.book_id==book.id)).first()
                    if suggestion:
                        suggestion.delete()
        else:
            print(mobile_number)