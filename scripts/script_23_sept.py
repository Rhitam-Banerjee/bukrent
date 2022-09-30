from app.models.books import Book
from app.models.format import Format
from app.models.publishers import Publisher

from sqlalchemy import and_

import csv

from app import db

def sept_23():
    # all_publishers = Publisher.query.all()

    # for publisher in all_publishers:
    #     publisher.age1 = False
    #     publisher.age2 = False
    #     publisher.age3 = False
    #     publisher.age4 = False
    #     publisher.age5 = False
    #     publisher.age6 = False
    #     publisher.display = False

    #     db.session.add(publisher)

    # db.session.commit()

    # display_publishers = [
    #     "Usborne Publishing Ltd",
    #     "Oxford University Press",
    #     "Walker Books Ltd",
    #     "Disney Press",
    #     "Scholastic",
    #     "DK",
    #     "Tiger Tales",
    #     "Penguin Random House Children's UK",
    #     "Pan Macmillan"
    # ]

    # for name in display_publishers:
    #     publisher_obj = Publisher.query.filter_by(name=name).first()
    #     publisher_obj.age1 = True
    #     publisher_obj.age2 = True
    #     publisher_obj.age3 = True
    #     publisher_obj.age4 = True
    #     publisher_obj.age5 = True
    #     publisher_obj.age6 = True
    #     publisher_obj.display = True

    #     db.session.add(publisher_obj)
    
    # db.session.commit()

    tags = []
    with open("scripts/data/23_sept/isbn.csv", mode="r") as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            tags.append(line)

    tags = tags[1:]

    for tag in tags:
        isbn = tag[1]

        book = Book.query.filter_by(isbn=isbn).first()

        if book:
            book.tag1 = tag[6]
            db.session.add(book)

            format_obj = Format.query.filter_by(name=tag[2]).first()

            format_obj.books.append(book)

            db.session.add(format_obj)

            db.session.commit()