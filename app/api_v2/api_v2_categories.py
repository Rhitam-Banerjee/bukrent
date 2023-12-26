from flask import jsonify, request

from sqlalchemy import and_, or_

from app import db
from app.models.new_books import NewBookSection, NewCategory,NewGenre

from app.api_v2.utils import api_v2_books

@api_v2_books.route('/get-categories')
def get_categories(): 
    age = request.args.get('age')
    start = request.args.get('start')
    end = request.args.get('end')
    search_query = request.args.get('search_query')
    if not start or not start.isnumeric(): 
        start = 0
    if not end or not end.isnumeric(): 
        end = 10
    start = int(start)
    end = int(end)
    categories_query = NewCategory.query
    if search_query: 
        categories_query = categories_query.filter(NewCategory.name.ilike(f'{search_query}%'))
    if age is not None and age.isnumeric(): 
        age = int(age)
        categories_query = categories_query.filter(
            NewCategory.min_age <= age, 
            NewCategory.max_age >= age
        )
    categories = [category.to_json() for category in categories_query.order_by(NewCategory.name).limit(end - start).offset(start).all()]
    print(len(categories))
    return jsonify({"success": True, "categories": categories})

@api_v2_books.route('/add-category', methods=['POST'])
def add_category(): 
    name = request.json.get('name')
    min_age = request.json.get('min_age')
    max_age = request.json.get('max_age')
    if not all((name, min_age, max_age)): 
        return jsonify({"success": False, "message": "Provide all the data"}), 400
    if not str(min_age).isnumeric() or not str(max_age).isnumeric() or int(min_age) > int(max_age): 
        return jsonify({"success": False, "message": "Invalid minimum and maximum age"}), 400
    if NewCategory.query.filter_by(name=name).count(): 
        return jsonify({"success": False, "message": "Category with the given name already exists"}), 400
    NewCategory.create(
        name, 
        100, 
        min_age, 
        max_age
    )
    category = NewCategory.query.filter_by(name=name).first().to_json()
    return jsonify({"success": True, "category": category})

@api_v2_books.route('/update-category', methods=['POST'])
def update_category(): 
    id = request.json.get('id')
    name = request.json.get('name')
    min_age = request.json.get('min_age')
    max_age = request.json.get('max_age')

    category = NewCategory.query.filter_by(id=id).first()

    if not category: 
        return jsonify({"success": False, "message": "Invalid category ID"}), 400
    if not name or min_age is None or max_age is None: 
        return jsonify({"success": False, "message": "Provide all the data"}), 400
    if not str(min_age).isnumeric() or not str(max_age).isnumeric() or int(min_age) > int(max_age): 
        return jsonify({"success": False, "message": "Invalid minimum and maximum age"}), 400
    
    category.name = name
    category.min_age = min_age
    category.max_age = max_age

    db.session.commit()

    return jsonify({"success": True, "category": category.to_json()})

@api_v2_books.route('/delete-category', methods=['POST'])
def delete_category(): 
    id = request.json.get('id')

    category = NewCategory.query.filter_by(id=id).first()
    if not category: 
        return jsonify({"success": False, "message": "Invalid category ID"}), 400
    category.delete()
    
    db.session.commit()

    return jsonify({"success": True})

@api_v2_books.route('/get-sections')
def get_sections(): 
    sections = [section.to_json() for section in NewBookSection.query.all()]
    return jsonify({"success": True, "sections": sections})

@api_v2_books.route('/get-genres')
def get_genres(): 
    age = request.args.get('age')

    if age:
        genres = NewGenre.query.filter(NewGenre.min_age <= age, NewGenre.max_age >= age).all()
    else:
        genres = NewGenre.query.all()

    genre_list = [{
        'id': genre.genre_id,
        'name': genre.genre_name,
        'min_age': genre.min_age,
        'max_age': genre.max_age
    } for genre in genres]

    return jsonify({"success": True, "genres": genre_list})

@api_v2_books.route('/update-genre/<string:genre_name>', methods=['POST'])
def update_genre_by_name(genre_name):
    genres = NewGenre.query.filter_by(genre_name=genre_name).all()
    if not genres:
        return jsonify({'error': 'No genres found with the given genre_name'}), 404

   
    updated_details = {}
    if 'name' in request.json:
        updated_details['genre_name'] = request.json['name']
    if 'min_age' in request.json:
        updated_details['min_age'] = request.json['min_age']
    if 'max_age' in request.json:
        updated_details['max_age'] = request.json['max_age']

    # Update details for all genres with the same genre_name
    for genre in genres:
        for field, value in updated_details.items():
            setattr(genre, field, value)

    db.session.commit()
    return jsonify({'message': f'Updated details for all genres with genre_name: {genre_name}'})

@api_v2_books.route('/delete-genre/<string:genre_name>', methods=['GET'])
def delete_genre_by_name(genre_name):
    genres = NewGenre.query.filter_by(genre_name=genre_name).all()
    if not genres:
        return jsonify({'error': 'No genres found with the given genre_name'}), 404

    for genre in genres:
        db.session.delete(genre)

    db.session.commit()
    return jsonify({'message': f'Deleted all genres with genre_name: {genre_name}'})

@api_v2_books.route('/create-genre', methods=['POST'])
def create_genre():
    
    genre_name = request.json.get('genre_name')
    min_age = request.json.get('min_age')
    max_age = request.json.get('max_age')

   
    if not (genre_name and min_age and max_age):
        return jsonify({'error': 'Incomplete data provided'}), 400

    new_genre = NewGenre(genre_name=genre_name, min_age=min_age, max_age=max_age)
    db.session.add(new_genre)
    db.session.commit()

    return jsonify({'message': 'New genre created successfully'})

