from flask import Blueprint, jsonify, request, render_template, redirect, session, url_for

from app.models.annotations import Annotation
from app.models.author import Author
from app.models.books import Book
from app.models.category import Category
from app.models.details import Detail
from app.models.publishers import Publisher
from app.models.reviews import Review
from app.models.series import Series

views = Blueprint('views', __name__, url_prefix="/")

@views.route("/")
def home():
    return render_template(
        "/launch/launch.html"
    )

@views.route("test")
def test():
    bestseller_books = Detail.get_bestsellers()
    bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]

    series = Series.get_top_series()

    authors = Author.get_top_authors()

    categories = Category.get_top_categories()

    publishers = Publisher.get_top_publishers()
    return render_template( 
        "/home/home.html",
        bestsellers=bestsellers,
        series=series,
        authors=authors,
        categories=categories,
        publishers=publishers
    )

@views.route("/book-details")
def book_details():
    guid = request.args.get("guid")
    book = Book.query.filter_by(guid=guid).first()

    more_books = Book.get_more_books(book.details)
    return render_template(
        "/details/detail.html",
        book=book,
        more_books=more_books
    )

@views.route('/category')
def book_category():
    age_group = request.args.get('age-group')
    category_type = request.args.get('type') #Bestseller, Author, Series, Genres, Publishers

    age_bracket = Detail.get_age_bracket(age_group)

    if age_group and not category_type:
        page_dict = {
            "section_1": {},
            "section_2": {},
            "section_3": {},
            "section_4": {},
            "section_5": {}
        }

        if age_group == "1":
            page_dict["section_1"]["title"] = f"Best Sellers for {age_bracket} Years"
            bestseller_books = Detail.get_bestsellers_for_age(age_group)
            bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
            page_dict["section_1"]["objs"] = bestsellers
            page_dict["section_1"]["type"] = "single"
            page_dict["section_1"]["url_type"] = "bestseller"

            authors = Author.query.order_by(Author.age1_books.desc()).limit(10).all()
            page_dict["section_2"]["title"] = f"Authors for {age_bracket} Years"
            page_dict["section_2"]["objs"] = authors
            page_dict["section_2"]["type"] = "multi"
            page_dict["section_2"]["url_type"] = "author"

            series = Series.query.order_by(Series.age1_books.desc()).limit(10).all()
            page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
            page_dict["section_3"]["objs"] = series
            page_dict["section_3"]["type"] = "multi"
            page_dict["section_3"]["url_type"] = "series"

            genres = Category.query.order_by(Category.age1_books.desc()).limit(10).all()
            page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
            page_dict["section_4"]["objs"] = genres
            page_dict["section_4"]["type"] = "multi"
            page_dict["section_4"]["url_type"] = "genre"

            publishers = Publisher.query.order_by(Publisher.age1_books.desc()).limit(10).all()
            page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
            page_dict["section_5"]["objs"] = publishers
            page_dict["section_5"]["type"] = "multi"
            page_dict["section_5"]["url_type"] = "publisher"
        
        elif age_group == "2":
            page_dict["section_1"]["title"] = f"Best Sellers for {age_bracket} Years"
            bestseller_books = Detail.get_bestsellers_for_age(age_group)
            bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
            page_dict["section_1"]["objs"] = bestsellers
            page_dict["section_1"]["type"] = "single"
            page_dict["section_1"]["url_type"] = "bestseller"

            authors = Author.query.order_by(Author.age2_books.desc()).limit(10).all()
            page_dict["section_2"]["title"] = f"Authors for {age_bracket} Years"
            page_dict["section_2"]["objs"] = authors
            page_dict["section_2"]["type"] = "multi"
            page_dict["section_2"]["url_type"] = "author"

            series = Series.query.order_by(Series.age2_books.desc()).limit(10).all()
            page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
            page_dict["section_3"]["objs"] = series
            page_dict["section_3"]["type"] = "multi"
            page_dict["section_3"]["url_type"] = "series"

            genres = Category.query.order_by(Category.age2_books.desc()).limit(10).all()
            page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
            page_dict["section_4"]["objs"] = genres
            page_dict["section_4"]["type"] = "multi"
            page_dict["section_4"]["url_type"] = "genre"

            publishers = Publisher.query.order_by(Publisher.age2_books.desc()).limit(10).all()
            page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
            page_dict["section_5"]["objs"] = publishers
            page_dict["section_5"]["type"] = "multi"
            page_dict["section_5"]["url_type"] = "publisher"

        elif age_group == "3":
            page_dict["section_1"]["title"] = f"Best Sellers for {age_bracket} Years"
            bestseller_books = Detail.get_bestsellers_for_age(age_group)
            bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
            page_dict["section_1"]["objs"] = bestsellers
            page_dict["section_1"]["type"] = "single"
            page_dict["section_1"]["url_type"] = "bestseller"

            authors = Author.query.order_by(Author.age3_books.desc()).limit(10).all()
            page_dict["section_2"]["title"] = f"Authors for {age_bracket} Years"
            page_dict["section_2"]["objs"] = authors
            page_dict["section_2"]["type"] = "multi"
            page_dict["section_2"]["url_type"] = "author"

            series = Series.query.order_by(Series.age3_books.desc()).limit(10).all()
            page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
            page_dict["section_3"]["objs"] = series
            page_dict["section_3"]["type"] = "multi"
            page_dict["section_3"]["url_type"] = "series"

            genres = Category.query.order_by(Category.age3_books.desc()).limit(10).all()
            page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
            page_dict["section_4"]["objs"] = genres
            page_dict["section_4"]["type"] = "multi"
            page_dict["section_4"]["url_type"] = "genre"

            publishers = Publisher.query.order_by(Publisher.age3_books.desc()).limit(10).all()
            page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
            page_dict["section_5"]["objs"] = publishers
            page_dict["section_5"]["type"] = "multi"
            page_dict["section_5"]["url_type"] = "publisher"

        elif age_group == "4":
            page_dict["section_1"]["title"] = f"Best Sellers for {age_bracket} Years"
            bestseller_books = Detail.get_bestsellers_for_age(age_group)
            bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
            page_dict["section_1"]["objs"] = bestsellers
            page_dict["section_1"]["type"] = "single"
            page_dict["section_1"]["url_type"] = "bestseller"

            authors = Author.query.order_by(Author.age4_books.desc()).limit(10).all()
            page_dict["section_2"]["title"] = f"Authors for {age_bracket} Years"
            page_dict["section_2"]["objs"] = authors
            page_dict["section_2"]["type"] = "multi"
            page_dict["section_2"]["url_type"] = "author"

            series = Series.query.order_by(Series.age4_books.desc()).limit(10).all()
            page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
            page_dict["section_3"]["objs"] = series
            page_dict["section_3"]["type"] = "multi"
            page_dict["section_3"]["url_type"] = "series"

            genres = Category.query.order_by(Category.age4_books.desc()).limit(10).all()
            page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
            page_dict["section_4"]["objs"] = genres
            page_dict["section_4"]["type"] = "multi"
            page_dict["section_4"]["url_type"] = "genre"

            publishers = Publisher.query.order_by(Publisher.age4_books.desc()).limit(10).all()
            page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
            page_dict["section_5"]["objs"] = publishers
            page_dict["section_5"]["type"] = "multi"
            page_dict["section_5"]["url_type"] = "publisher"

        else:
            page_dict["section_1"]["title"] = f"Best Sellers for {age_bracket} Years"
            bestseller_books = Detail.get_bestsellers_for_age(age_group)
            bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
            page_dict["section_1"]["objs"] = bestsellers
            page_dict["section_1"]["type"] = "single"
            page_dict["section_1"]["url_type"] = "bestseller"

            authors = Author.query.order_by(Author.age5_books.desc()).limit(10).all()
            page_dict["section_2"]["title"] = f"Authors for {age_bracket} Years"
            page_dict["section_2"]["objs"] = authors
            page_dict["section_2"]["type"] = "multi"
            page_dict["section_2"]["url_type"] = "author"

            series = Series.query.order_by(Series.age5_books.desc()).limit(10).all()
            page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
            page_dict["section_3"]["objs"] = series
            page_dict["section_3"]["type"] = "multi"
            page_dict["section_3"]["url_type"] = "series"

            genres = Category.query.order_by(Category.age5_books.desc()).limit(10).all()
            page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
            page_dict["section_4"]["objs"] = genres
            page_dict["section_4"]["type"] = "multi"
            page_dict["section_4"]["url_type"] = "genre"

            publishers = Publisher.query.order_by(Publisher.age5_books.desc()).limit(10).all()
            page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
            page_dict["section_5"]["objs"] = publishers
            page_dict["section_5"]["type"] = "multi"
            page_dict["section_5"]["url_type"] = "publisher"

    elif category_type and not age_group:
        page_dict = {
            "section_1": {},
            "section_2": {},
            "section_3": {},
            "section_4": {},
            "section_5": {}
        }

        if category_type == "bestseller":
            page_dict["section_1"]["title"] = f"Best Sellers"
            bestseller_books = Detail.get_bestsellers()
            bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
            page_dict["section_1"]["objs"] = bestsellers
            page_dict["section_1"]["type"] = "single"
            page_dict["section_1"]["url_type"] = "bestseller"

            authors = Author.query.order_by(Author.total_books.desc()).limit(10).all()
            page_dict["section_2"]["title"] = f"Authors"
            page_dict["section_2"]["objs"] = authors
            page_dict["section_2"]["type"] = "multi"
            page_dict["section_2"]["url_type"] = "author"

            series = Series.query.order_by(Series.total_books.desc()).limit(10).all()
            page_dict["section_3"]["title"] = f"Series"
            page_dict["section_3"]["objs"] = series
            page_dict["section_3"]["type"] = "multi"
            page_dict["section_3"]["url_type"] = "series"

            genres = Category.query.order_by(Category.total_books.desc()).limit(10).all()
            page_dict["section_4"]["title"] = f"Genres"
            page_dict["section_4"]["objs"] = genres
            page_dict["section_4"]["type"] = "multi"
            page_dict["section_4"]["url_type"] = "genre"

            publishers = Publisher.query.order_by(Publisher.total_books.desc()).limit(10).all()
            page_dict["section_5"]["title"] = f"Publishers"
            page_dict["section_5"]["objs"] = publishers
            page_dict["section_5"]["type"] = "multi"
            page_dict["section_5"]["url_type"] = "publisher"

        elif category_type == "series":
            page_dict["section_3"]["title"] = f"Best Sellers"
            bestseller_books = Detail.get_bestsellers()
            bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
            page_dict["section_3"]["objs"] = bestsellers
            page_dict["section_3"]["type"] = "single"
            page_dict["section_3"]["url_type"] = "bestseller"

            authors = Author.query.order_by(Author.total_books.desc()).limit(10).all()
            page_dict["section_2"]["title"] = f"Authors"
            page_dict["section_2"]["objs"] = authors
            page_dict["section_2"]["type"] = "multi"
            page_dict["section_2"]["url_type"] = "author"

            series = Series.query.order_by(Series.total_books.desc()).limit(10).all()
            page_dict["section_1"]["title"] = f"Series"
            page_dict["section_1"]["objs"] = series
            page_dict["section_1"]["type"] = "multi"
            page_dict["section_1"]["url_type"] = "series"

            genres = Category.query.order_by(Category.total_books.desc()).limit(10).all()
            page_dict["section_4"]["title"] = f"Genres"
            page_dict["section_4"]["objs"] = genres
            page_dict["section_4"]["type"] = "multi"
            page_dict["section_4"]["url_type"] = "genre"

            publishers = Publisher.query.order_by(Publisher.total_books.desc()).limit(10).all()
            page_dict["section_5"]["title"] = f"Publishers"
            page_dict["section_5"]["objs"] = publishers
            page_dict["section_5"]["type"] = "multi"
            page_dict["section_5"]["url_type"] = "publisher"

        elif category_type == "authors":
            page_dict["section_2"]["title"] = f"Best Sellers"
            bestseller_books = Detail.get_bestsellers()
            bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
            page_dict["section_2"]["objs"] = bestsellers
            page_dict["section_2"]["type"] = "single"
            page_dict["section_2"]["url_type"] = "bestseller"

            authors = Author.query.order_by(Author.total_books.desc()).limit(10).all()
            page_dict["section_1"]["title"] = f"Authors"
            page_dict["section_1"]["objs"] = authors
            page_dict["section_1"]["type"] = "multi"
            page_dict["section_1"]["url_type"] = "author"

            series = Series.query.order_by(Series.total_books.desc()).limit(10).all()
            page_dict["section_3"]["title"] = f"Series"
            page_dict["section_3"]["objs"] = series
            page_dict["section_3"]["type"] = "multi"
            page_dict["section_3"]["url_type"] = "series"

            genres = Category.query.order_by(Category.total_books.desc()).limit(10).all()
            page_dict["section_4"]["title"] = f"Genres"
            page_dict["section_4"]["objs"] = genres
            page_dict["section_4"]["type"] = "multi"
            page_dict["section_4"]["url_type"] = "genre"

            publishers = Publisher.query.order_by(Publisher.total_books.desc()).limit(10).all()
            page_dict["section_5"]["title"] = f"Publishers"
            page_dict["section_5"]["objs"] = publishers
            page_dict["section_5"]["type"] = "multi"
            page_dict["section_5"]["url_type"] = "publisher"

        elif category_type == "genres":
            page_dict["section_4"]["title"] = f"Best Sellers"
            bestseller_books = Detail.get_bestsellers()
            bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
            page_dict["section_4"]["objs"] = bestsellers
            page_dict["section_4"]["type"] = "single"
            page_dict["section_4"]["url_type"] = "bestseller"

            authors = Author.query.order_by(Author.total_books.desc()).limit(10).all()
            page_dict["section_2"]["title"] = f"Authors"
            page_dict["section_2"]["objs"] = authors
            page_dict["section_2"]["type"] = "multi"
            page_dict["section_2"]["url_type"] = "author"

            series = Series.query.order_by(Series.total_books.desc()).limit(10).all()
            page_dict["section_3"]["title"] = f"Series"
            page_dict["section_3"]["objs"] = series
            page_dict["section_3"]["type"] = "multi"
            page_dict["section_3"]["url_type"] = "series"

            genres = Category.query.order_by(Category.total_books.desc()).limit(10).all()
            page_dict["section_1"]["title"] = f"Genres"
            page_dict["section_1"]["objs"] = genres
            page_dict["section_1"]["type"] = "multi"
            page_dict["section_1"]["url_type"] = "genre"

            publishers = Publisher.query.order_by(Publisher.total_books.desc()).limit(10).all()
            page_dict["section_5"]["title"] = f"Publishers"
            page_dict["section_5"]["objs"] = publishers
            page_dict["section_5"]["type"] = "multi"
            page_dict["section_5"]["url_type"] = "publisher"

        elif category_type == "publisher":
            page_dict["section_5"]["title"] = f"Best Sellers"
            bestseller_books = Detail.get_bestsellers()
            bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
            page_dict["section_5"]["objs"] = bestsellers
            page_dict["section_5"]["type"] = "single"
            page_dict["section_5"]["url_type"] = "bestseller"

            authors = Author.query.order_by(Author.total_books.desc()).limit(10).all()
            page_dict["section_2"]["title"] = f"Authors"
            page_dict["section_2"]["objs"] = authors
            page_dict["section_2"]["type"] = "multi"
            page_dict["section_2"]["url_type"] = "author"

            series = Series.query.order_by(Series.total_books.desc()).limit(10).all()
            page_dict["section_3"]["title"] = f"Series"
            page_dict["section_3"]["objs"] = series
            page_dict["section_3"]["type"] = "multi"
            page_dict["section_3"]["url_type"] = "series"

            genres = Category.query.order_by(Category.total_books.desc()).limit(10).all()
            page_dict["section_4"]["title"] = f"Genres"
            page_dict["section_4"]["objs"] = genres
            page_dict["section_4"]["type"] = "multi"
            page_dict["section_4"]["url_type"] = "genre"

            publishers = Publisher.query.order_by(Publisher.total_books.desc()).limit(10).all()
            page_dict["section_1"]["title"] = f"Publishers"
            page_dict["section_1"]["objs"] = publishers
            page_dict["section_1"]["type"] = "multi"
            page_dict["section_1"]["url_type"] = "publisher"

    elif category_type and age_group:
        page_dict = {
            "section_1": {},
            "section_2": {},
            "section_3": {},
            "section_4": {},
            "section_5": {}
        }

        if category_type == "bestseller":
            if age_group == "1":
                page_dict["section_1"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_1"]["objs"] = bestsellers
                page_dict["section_1"]["type"] = "single"
                page_dict["section_1"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age1_books.desc()).limit(10).all()
                page_dict["section_2"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_2"]["objs"] = authors
                page_dict["section_2"]["type"] = "multi"
                page_dict["section_2"]["url_type"] = "author"

                series = Series.query.order_by(Series.age1_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age1_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_4"]["objs"] = genres
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age1_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

            elif age_group == "2":
                page_dict["section_1"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_1"]["objs"] = bestsellers
                page_dict["section_1"]["type"] = "single"
                page_dict["section_1"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age2_books.desc()).limit(10).all()
                page_dict["section_2"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_2"]["objs"] = authors
                page_dict["section_2"]["type"] = "multi"
                page_dict["section_2"]["url_type"] = "author"

                series = Series.query.order_by(Series.age2_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age2_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_4"]["objs"] = genres
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age2_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

            elif age_group == "3":
                page_dict["section_1"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_1"]["objs"] = bestsellers
                page_dict["section_1"]["type"] = "single"
                page_dict["section_1"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age3_books.desc()).limit(10).all()
                page_dict["section_2"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_2"]["objs"] = authors
                page_dict["section_2"]["type"] = "multi"
                page_dict["section_2"]["url_type"] = "author"

                series = Series.query.order_by(Series.age3_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age3_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_4"]["objs"] = genres
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age3_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

            elif age_group == "4":
                page_dict["section_1"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_1"]["objs"] = bestsellers
                page_dict["section_1"]["type"] = "single"
                page_dict["section_1"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age4_books.desc()).limit(10).all()
                page_dict["section_2"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_2"]["objs"] = authors
                page_dict["section_2"]["type"] = "multi"
                page_dict["section_2"]["url_type"] = "author"

                series = Series.query.order_by(Series.age4_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age4_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_4"]["objs"] = genres
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age4_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

            else:
                page_dict["section_1"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_1"]["objs"] = bestsellers
                page_dict["section_1"]["type"] = "single"
                page_dict["section_1"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age5_books.desc()).limit(10).all()
                page_dict["section_2"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_2"]["objs"] = authors
                page_dict["section_2"]["type"] = "multi"
                page_dict["section_2"]["url_type"] = "author"

                series = Series.query.order_by(Series.age5_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age5_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_4"]["objs"] = genres
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age5_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

        elif category_type == "series":
            if age_group == "1":
                page_dict["section_3"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_3"]["objs"] = bestsellers
                page_dict["section_3"]["type"] = "single"
                page_dict["section_3"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age1_books.desc()).limit(10).all()
                page_dict["section_2"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_2"]["objs"] = authors
                page_dict["section_2"]["type"] = "multi"
                page_dict["section_2"]["url_type"] = "author"

                series = Series.query.order_by(Series.age1_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_1"]["objs"] = series
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age1_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_4"]["objs"] = genres
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age1_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

            elif age_group == "2":
                page_dict["section_3"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_3"]["objs"] = bestsellers
                page_dict["section_3"]["type"] = "single"
                page_dict["section_3"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age2_books.desc()).limit(10).all()
                page_dict["section_2"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_2"]["objs"] = authors
                page_dict["section_2"]["type"] = "multi"
                page_dict["section_2"]["url_type"] = "author"

                series = Series.query.order_by(Series.age2_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_1"]["objs"] = series
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age2_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_4"]["objs"] = genres
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age2_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

            elif age_group == "3":
                page_dict["section_3"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_3"]["objs"] = bestsellers
                page_dict["section_3"]["type"] = "single"
                page_dict["section_3"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age3_books.desc()).limit(10).all()
                page_dict["section_2"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_2"]["objs"] = authors
                page_dict["section_2"]["type"] = "multi"
                page_dict["section_2"]["url_type"] = "author"

                series = Series.query.order_by(Series.age3_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_1"]["objs"] = series
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age3_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_4"]["objs"] = genres
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age3_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

            elif age_group == "4":
                page_dict["section_3"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_3"]["objs"] = bestsellers
                page_dict["section_3"]["type"] = "single"
                page_dict["section_3"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age4_books.desc()).limit(10).all()
                page_dict["section_2"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_2"]["objs"] = authors
                page_dict["section_2"]["type"] = "multi"
                page_dict["section_2"]["url_type"] = "author"

                series = Series.query.order_by(Series.age4_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_1"]["objs"] = series
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age4_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_4"]["objs"] = genres
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age4_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

            else:
                page_dict["section_3"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_3"]["objs"] = bestsellers
                page_dict["section_3"]["type"] = "single"
                page_dict["section_3"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age5_books.desc()).limit(10).all()
                page_dict["section_2"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_2"]["objs"] = authors
                page_dict["section_2"]["type"] = "multi"
                page_dict["section_2"]["url_type"] = "author"

                series = Series.query.order_by(Series.age5_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_1"]["objs"] = series
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age5_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_4"]["objs"] = genres
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age5_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

        elif category_type == "authors":
            if age_group == "1":
                page_dict["section_2"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_2"]["objs"] = bestsellers
                page_dict["section_2"]["type"] = "single"
                page_dict["section_2"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age1_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_1"]["objs"] = authors
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "author"

                series = Series.query.order_by(Series.age1_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age1_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_4"]["objs"] = genres
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age1_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

            elif age_group == "2":
                page_dict["section_2"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_2"]["objs"] = bestsellers
                page_dict["section_2"]["type"] = "single"
                page_dict["section_2"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age2_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_1"]["objs"] = authors
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "author"

                series = Series.query.order_by(Series.age2_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age2_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_4"]["objs"] = genres
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age2_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

            elif age_group == "3":
                page_dict["section_2"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_2"]["objs"] = bestsellers
                page_dict["section_2"]["type"] = "single"
                page_dict["section_2"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age3_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_1"]["objs"] = authors
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "author"

                series = Series.query.order_by(Series.age3_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age3_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_4"]["objs"] = genres
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age3_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

            elif age_group == "4":
                page_dict["section_2"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_2"]["objs"] = bestsellers
                page_dict["section_2"]["type"] = "single"
                page_dict["section_2"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age4_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_1"]["objs"] = authors
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "author"

                series = Series.query.order_by(Series.age4_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age4_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_4"]["objs"] = genres
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age4_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

            else:
                page_dict["section_2"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_2"]["objs"] = bestsellers
                page_dict["section_2"]["type"] = "single"
                page_dict["section_2"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age5_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_1"]["objs"] = authors
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "author"

                series = Series.query.order_by(Series.age5_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age5_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_4"]["objs"] = genres
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age5_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

        elif category_type == "genres":
            if age_group == "1":
                page_dict["section_2"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_2"]["objs"] = bestsellers
                page_dict["section_2"]["type"] = "single"
                page_dict["section_2"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age1_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_4"]["objs"] = authors
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "author"

                series = Series.query.order_by(Series.age1_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age1_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_1"]["objs"] = genres
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age1_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

            elif age_group == "2":
                page_dict["section_2"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_2"]["objs"] = bestsellers
                page_dict["section_2"]["type"] = "single"
                page_dict["section_2"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age2_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_4"]["objs"] = authors
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "author"

                series = Series.query.order_by(Series.age2_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age2_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_1"]["objs"] = genres
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age2_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

            elif age_group == "3":
                page_dict["section_2"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_2"]["objs"] = bestsellers
                page_dict["section_2"]["type"] = "single"
                page_dict["section_2"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age3_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_4"]["objs"] = authors
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "author"

                series = Series.query.order_by(Series.age3_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age3_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_1"]["objs"] = genres
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age3_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

            elif age_group == "4":
                page_dict["section_2"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_2"]["objs"] = bestsellers
                page_dict["section_2"]["type"] = "single"
                page_dict["section_2"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age4_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_4"]["objs"] = authors
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "author"

                series = Series.query.order_by(Series.age4_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age4_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_1"]["objs"] = genres
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age4_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

            else:
                page_dict["section_2"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_2"]["objs"] = bestsellers
                page_dict["section_2"]["type"] = "single"
                page_dict["section_2"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age5_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_4"]["objs"] = authors
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "author"

                series = Series.query.order_by(Series.age5_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age5_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_1"]["objs"] = genres
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age5_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_5"]["objs"] = publishers
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "publisher"

        elif category_type == "publisher":
            if age_group == "1":
                page_dict["section_2"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_2"]["objs"] = bestsellers
                page_dict["section_2"]["type"] = "single"
                page_dict["section_2"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age1_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_4"]["objs"] = authors
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "author"

                series = Series.query.order_by(Series.age1_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age1_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_5"]["objs"] = genres
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age1_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_1"]["objs"] = publishers
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "publisher"

            elif age_group == "2":
                page_dict["section_2"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_2"]["objs"] = bestsellers
                page_dict["section_2"]["type"] = "single"
                page_dict["section_2"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age2_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_4"]["objs"] = authors
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "author"

                series = Series.query.order_by(Series.age2_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age2_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_5"]["objs"] = genres
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age2_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_1"]["objs"] = publishers
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "publisher"

            elif age_group == "3":
                page_dict["section_2"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_2"]["objs"] = bestsellers
                page_dict["section_2"]["type"] = "single"
                page_dict["section_2"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age3_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_4"]["objs"] = authors
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "author"

                series = Series.query.order_by(Series.age3_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age3_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_5"]["objs"] = genres
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age3_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_1"]["objs"] = publishers
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "publisher"

            elif age_group == "4":
                page_dict["section_2"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_2"]["objs"] = bestsellers
                page_dict["section_2"]["type"] = "single"
                page_dict["section_2"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age4_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_4"]["objs"] = authors
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "author"

                series = Series.query.order_by(Series.age4_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age4_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_5"]["objs"] = genres
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age4_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_1"]["objs"] = publishers
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "publisher"

            else:
                page_dict["section_2"]["title"] = f"Best Sellers for {age_bracket} Years"
                bestseller_books = Detail.get_bestsellers_for_age(age_group)
                bestsellers = [Book.query.filter_by(id=book_id).first() for book_id in bestseller_books]
                page_dict["section_2"]["objs"] = bestsellers
                page_dict["section_2"]["type"] = "single"
                page_dict["section_2"]["url_type"] = "bestseller"

                authors = Author.query.order_by(Author.age5_books.desc()).limit(10).all()
                page_dict["section_4"]["title"] = f"Authors for {age_bracket} Years"
                page_dict["section_4"]["objs"] = authors
                page_dict["section_4"]["type"] = "multi"
                page_dict["section_4"]["url_type"] = "author"

                series = Series.query.order_by(Series.age5_books.desc()).limit(10).all()
                page_dict["section_3"]["title"] = f"Series for {age_bracket} Years"
                page_dict["section_3"]["objs"] = series
                page_dict["section_3"]["type"] = "multi"
                page_dict["section_3"]["url_type"] = "series"

                genres = Category.query.order_by(Category.age5_books.desc()).limit(10).all()
                page_dict["section_5"]["title"] = f"Genres for {age_bracket} Years"
                page_dict["section_5"]["objs"] = genres
                page_dict["section_5"]["type"] = "multi"
                page_dict["section_5"]["url_type"] = "genre"

                publishers = Publisher.query.order_by(Publisher.age5_books.desc()).limit(10).all()
                page_dict["section_1"]["title"] = f"Publishers for {age_bracket} Years"
                page_dict["section_1"]["objs"] = publishers
                page_dict["section_1"]["type"] = "multi"
                page_dict["section_1"]["url_type"] = "publisher"

    return render_template(
        "/category/category.html",
        age_group=age_group,
        page_dict=page_dict
    )

@views.route('/sub-category')
def book_subcategory():
    guid = request.args.get("guid")
    category_type = request.args.get('type')
    age_group = request.args.get("age-group")

    age_bracket = Detail.get_age_bracket(age_group)

    page_dict = {
        "section_1": {},
        "section_2": {},
        "section_3": {},
        "section_4": {}
    }

    if category_type == "author":
        main_obj = Author.query.filter_by(guid=guid).first()
        if age_group:
            if age_group == "1":
                authors = Author.query.order_by(Author.age1_books.desc()).limit(4).all()
            elif age_group == "2":
                authors = Author.query.order_by(Author.age2_books.desc()).limit(4).all()
            elif age_group == "3":
                authors = Author.query.order_by(Author.age3_books.desc()).limit(4).all()
            elif age_group == "4":
                authors = Author.query.order_by(Author.age4_books.desc()).limit(4).all()
            else:
                authors = Author.query.order_by(Author.age5_books.desc()).limit(4).all()
            page_dict["section_1"]["title"] = f"Books by {authors[0].name} for {age_bracket} Years"
            page_dict["section_2"]["title"] = f"Books by {authors[1].name} for {age_bracket} Years"
            page_dict["section_3"]["title"] = f"Books by {authors[2].name} for {age_bracket} Years"
            page_dict["section_4"]["title"] = f"Books by {authors[3].name} for {age_bracket} Years"
        else:
            authors = Author.query.order_by(Author.total_books.desc()).limit(4).all()
            page_dict["section_1"]["title"] = f"Books by {authors[0].name}"
            page_dict["section_2"]["title"] = f"Books by {authors[1].name}"
            page_dict["section_3"]["title"] = f"Books by {authors[2].name}"
            page_dict["section_4"]["title"] = f"Books by {authors[3].name}"
        page_dict["section_1"]["objs"] = authors[0].books[:10]
        page_dict["section_2"]["objs"] = authors[1].books[:10]
        page_dict["section_3"]["objs"] = authors[2].books[:10]
        page_dict["section_4"]["objs"] = authors[3].books[:10]
    elif category_type == "series":
        main_obj = Series.query.filter_by(guid=guid).first()
        if age_group:
            if age_group == "1":
                series = Series.query.order_by(Series.age1_books.desc()).limit(4).all()
            elif age_group == "2":
                series = Series.query.order_by(Series.age2_books.desc()).limit(4).all()
            elif age_group == "3":
                series = Series.query.order_by(Series.age3_books.desc()).limit(4).all()
            elif age_group == "4":
                series = Series.query.order_by(Series.age4_books.desc()).limit(4).all()
            else:
                series = Series.query.order_by(Series.age5_books.desc()).limit(4).all()
            page_dict["section_1"]["title"] = f"Books in {series[0].name} for {age_bracket} Years"
            page_dict["section_2"]["title"] = f"Books in {series[1].name} for {age_bracket} Years"
            page_dict["section_3"]["title"] = f"Books in {series[2].name} for {age_bracket} Years"
            page_dict["section_4"]["title"] = f"Books in {series[3].name} for {age_bracket} Years"
        else:
            series = Series.query.order_by(Series.total_books.desc()).limit(4).all()
            page_dict["section_1"]["title"] = f"Books in {series[0].name}"
            page_dict["section_2"]["title"] = f"Books in {series[1].name}"
            page_dict["section_3"]["title"] = f"Books in {series[2].name}"
            page_dict["section_4"]["title"] = f"Books in {series[3].name}"
        page_dict["section_1"]["objs"] = series[0].books[:10]
        page_dict["section_2"]["objs"] = series[1].books[:10]
        page_dict["section_3"]["objs"] = series[2].books[:10]
        page_dict["section_4"]["objs"] = series[3].books[:10]
    elif category_type == "genres":
        main_obj = Category.query.filter_by(guid=guid).first()
        if age_group:
            if age_group == "1":
                categories = Category.query.order_by(Category.age1_books.desc()).limit(4).all()
            elif age_group == "2":
                categories = Category.query.order_by(Category.age2_books.desc()).limit(4).all()
            elif age_group == "3":
                categories = Category.query.order_by(Category.age3_books.desc()).limit(4).all()
            elif age_group == "4":
                categories = Category.query.order_by(Category.age4_books.desc()).limit(4).all()
            else:
                categories = Category.query.order_by(Category.age5_books.desc()).limit(4).all()
            page_dict["section_1"]["title"] = f"Books in {categories[0].name} for {age_bracket} Years"
            page_dict["section_2"]["title"] = f"Books in {categories[1].name} for {age_bracket} Years"
            page_dict["section_3"]["title"] = f"Books in {categories[2].name} for {age_bracket} Years"
            page_dict["section_4"]["title"] = f"Books in {categories[3].name} for {age_bracket} Years"
        else:
            categories = Category.query.order_by(Category.total_books.desc()).limit(4).all()
            page_dict["section_1"]["title"] = f"Books in {categories[0].name}"
            page_dict["section_2"]["title"] = f"Books in {categories[1].name}"
            page_dict["section_3"]["title"] = f"Books in {categories[2].name}"
            page_dict["section_4"]["title"] = f"Books in {categories[3].name}"
        page_dict["section_1"]["objs"] = categories[0].books[:10]
        page_dict["section_2"]["objs"] = categories[1].books[:10]
        page_dict["section_3"]["objs"] = categories[2].books[:10]
        page_dict["section_4"]["objs"] = categories[3].books[:10]
    elif category_type == "publisher":
        main_obj = Publisher.query.filter_by(guid=guid).first()
        if age_group:
            if age_group == "1":
                publishers = Publisher.query.order_by(Publisher.age1_books.desc()).limit(4).all()
            elif age_group == "2":
                publishers = Publisher.query.order_by(Publisher.age2_books.desc()).limit(4).all()
            elif age_group == "3":
                publishers = Publisher.query.order_by(Publisher.age3_books.desc()).limit(4).all()
            elif age_group == "4":
                publishers = Publisher.query.order_by(Publisher.age4_books.desc()).limit(4).all()
            else:
                publishers = Publisher.query.order_by(Publisher.age5_books.desc()).limit(4).all()
            page_dict["section_1"]["title"] = f"Books in {publishers[0].name} for {age_bracket} Years"
            page_dict["section_2"]["title"] = f"Books in {publishers[1].name} for {age_bracket} Years"
            page_dict["section_3"]["title"] = f"Books in {publishers[2].name} for {age_bracket} Years"
            page_dict["section_4"]["title"] = f"Books in {publishers[3].name} for {age_bracket} Years"
        else:
            publishers = Publisher.query.order_by(Publisher.total_books.desc()).limit(4).all()
            page_dict["section_1"]["title"] = f"Books in {publishers[0].name}"
            page_dict["section_2"]["title"] = f"Books in {publishers[1].name}"
            page_dict["section_3"]["title"] = f"Books in {publishers[2].name}"
            page_dict["section_4"]["title"] = f"Books in {publishers[3].name}"
        page_dict["section_1"]["objs"] = publishers[0].books[:10]
        page_dict["section_2"]["objs"] = publishers[1].books[:10]
        page_dict["section_3"]["objs"] = publishers[2].books[:10]
        page_dict["section_4"]["objs"] = publishers[3].books[:10]

    return render_template(
        "/sub_category/sub_category.html",
        age_group=age_group,
        page_dict=page_dict,
        main_obj=main_obj
    )

@views.route('/become-subscriber')
def become_a_subscriber():
    return render_template(
        "/become_subscriber/become_subscriber.html"
    )

@views.route('/confirm-plan')
def confirm_plan():
    plan = request.args.get("plan")
    if plan == "1":
        weekly_books = 1
        monthly_books = 4
        price_month = 299
    elif plan == "2":
        weekly_books = 2
        monthly_books = 8
        price_month = 499
    elif plan == "3":
        weekly_books = 4
        monthly_books = 16
        price_month = 749
    else:
        weekly_books = 6
        monthly_books = 24
        price_month = 949
    security_deposit = 500
    total_payable_amount = price_month + security_deposit

    session["plan"] = plan

    return render_template(
        "/confirm_plan/confirm_plan.html",
        weekly_books=weekly_books,
        monthly_books=monthly_books,
        price_month=price_month,
        security_deposit=security_deposit,
        total_payable_amount=total_payable_amount,
        plan=plan
    )

@views.route("/signup")
def signup():
    return render_template(
        "/signup/signup.html"
    )

@views.route("/confirm-mobile")
def confirm_mobile():
    mobile_number = session.get("mobile_number")
    return render_template(
        "/confirm_mobile/confirm_mobile.html",
        mobile_number=mobile_number
    )

@views.route("/subscribe")
def subscribe():
    selected_plan = session.get("plan")
    if not selected_plan:
        return redirect(url_for('views.become_a_subscriber'))
    return render_template(
        "/subscribe/subscribe.html"
    )

@views.route("/payment-successful")
def payment_successful():
    return render_template(
        "/payment_successful/payment_successful.html"
    )