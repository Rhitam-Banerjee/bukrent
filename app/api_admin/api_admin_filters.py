from flask import jsonify, request

from app import db
from app.models.books import Book, BookAuthor, BookPublisher, BookFormat
from app.models.author import Author
from app.models.publishers import Publisher
from app.models.series import Series
from app.models.format import Format

from app.api_admin.utils import api_admin, token_required


@api_admin.route('/add-author', methods=['POST'])
@token_required
def add_author(admin): 
    name = request.json.get('name')
    age_groups = request.json.get('age_groups')
    image = request.json.get('display')
    if not name: 
        return jsonify({"success": False, "message": "Provide a name"})
    if not age_groups or type(age_groups) != type([]) or len(age_groups) < 6: 
        return jsonify({"success": False, "message": "Age groups are required"})
    display = False
    if image: 
        display = True
    ages = [bool(age) for age in age_groups[:6]]
    Author.create(name, 'author', ages[0], ages[1], ages[2], ages[3], ages[4], ages[5], 0, display)
    return jsonify({"success": True})

@api_admin.route('/add-publisher', methods=['POST'])
@token_required
def add_publisher(admin): 
    name = request.json.get('name')
    age_groups = request.json.get('age_groups')
    image = request.json.get('display')
    if not name: 
        return jsonify({"success": False, "message": "Provide a name"})
    if not age_groups or type(age_groups) != type([]) or len(age_groups) < 6: 
        return jsonify({"success": False, "message": "Age groups are required"})
    display = False
    if image: 
        display = True
    ages = [bool(age) for age in age_groups[:6]]
    Publisher.create(name, ages[0], ages[1], ages[2], ages[3], ages[4], ages[5], 0, display)
    return jsonify({"success": True})

@api_admin.route('/add-series', methods=['POST'])
@token_required
def add_series(admin): 
    name = request.json.get('name')
    age_groups = request.json.get('age_groups')
    image = request.json.get('display')
    if not name: 
        return jsonify({"success": False, "message": "Provide a name"})
    if not age_groups or type(age_groups) != type([]) or len(age_groups) < 6: 
        return jsonify({"success": False, "message": "Age groups are required"})
    display = False
    if image: 
        display = True
    ages = [bool(age) for age in age_groups[:6]]
    Series.create(name, ages[0], ages[1], ages[2], ages[3], ages[4], ages[5], 0, display)
    return jsonify({"success": True})

@api_admin.route('/add-format', methods=['POST'])
@token_required
def add_format(admin): 
    name = request.json.get('name')
    age_groups = request.json.get('age_groups')
    image = request.json.get('display')
    if not name: 
        return jsonify({"success": False, "message": "Provide a name"})
    if not age_groups or type(age_groups) != type([]) or len(age_groups) < 6: 
        return jsonify({"success": False, "message": "Age groups are required"})
    display = False
    if image: 
        display = True
    ages = [bool(age) for age in age_groups[:6]]
    Format.create(name, ages[0], ages[1], ages[2], ages[3], ages[4], ages[5], 0, display)
    return jsonify({"success": True})

@api_admin.route('/delete-author', methods=['POST'])
@token_required
def delete_author(admin): 
    guid = request.json.get('guid')
    if not guid: 
        return jsonify({"success": False, "message": "Provide an author ID"})
    author = Author.query.filter_by(guid=guid).first()
    if not author: 
        return jsonify({"success": False, "message": "Invalid author ID"})
    book_authors = BookAuthor.query.filter_by(author_id=author.id).all()
    for book_author in book_authors: 
        db.session.delete(book_author)
    db.session.delete(author)
    db.session.commit()
    return jsonify({"success": True})

@api_admin.route('/delete-publisher', methods=['POST'])
@token_required
def delete_publisher(admin): 
    guid = request.json.get('guid')
    if not guid: 
        return jsonify({"success": False, "message": "Provide a publisher ID"})
    publisher = Publisher.query.filter_by(guid=guid).first()
    if not publisher: 
        return jsonify({"success": False, "message": "Invalid publisher ID"})
    book_publishers = BookPublisher.query.filter_by(publisher_id=publisher.id).all()
    for book_publisher in book_publishers: 
        db.session.delete(book_publisher)
    db.session.delete(publisher)
    db.session.commit()
    return jsonify({"success": True})

@api_admin.route('/delete-format', methods=['POST'])
@token_required
def delete_format(admin): 
    guid = request.json.get('guid')
    if not guid: 
        return jsonify({"success": False, "message": "Provide a format ID"})
    format = Format.query.filter_by(guid=guid).first()
    if not format: 
        return jsonify({"success": False, "message": "Invalid format ID"})
    book_formats = BookFormat.query.filter_by(format_id=format.id).all()
    for book_format in book_formats: 
        db.session.delete(book_format)
    db.session.delete(format)
    db.session.commit()
    return jsonify({"success": True})

@api_admin.route('/delete-series', methods=['POST'])
@token_required
def delete_series(admin): 
    guid = request.json.get('guid')
    if not guid: 
        return jsonify({"success": False, "message": "Provide a series ID"})
    series = Series.query.filter_by(guid=guid).first()
    if not series: 
        return jsonify({"success": False, "message": "Invalid series ID"})
    books = Book.query.filter_by(series_id=series.id).all()
    for book in books: 
        book.series_id = None
    db.session.delete(series)
    db.session.commit()
    return jsonify({"success": True})