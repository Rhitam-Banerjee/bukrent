from app import db
import uuid
from app.models.books import Book

class NewBookSection(db.Model): 
    __tablename__ = 'new_book_sections'
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False, unique=True)

    @staticmethod
    def create(name): 
        if NewBookSection.query.filter_by(name=name).count(): 
            return
        book_section_dict = dict(
            guid=str(uuid.uuid4()),
            name=name
        )
        new_book_section_obj = NewBookSection(**book_section_dict)
        db.session.add(new_book_section_obj)
        db.session.commit()

    def to_json(self): 
        return {
            "id": self.id,
            "guid": self.guid,
            "name": self.name,
        }

class NewCategoryBook(db.Model): 
    __tablename__ = 'new_category_books'
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('new_categories.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('new_books.id'))
    section_id = db.Column(db.Integer, db.ForeignKey('new_book_sections.id'))

    @staticmethod
    def create(category_id, book_id, section_id): 
        if NewCategoryBook.query.filter_by(category_id=category_id, book_id=book_id, section_id=section_id).count(): 
            return
        try: 
            category_book_dict = dict(
                guid=str(uuid.uuid4()),
                category_id=category_id,
                book_id=book_id,
                section_id=section_id
            )
            new_category_book_obj = NewCategoryBook(**category_book_dict)
            db.session.add(new_category_book_obj)
            db.session.commit()
        except: 
            pass

    def delete(self): 
        db.session.delete(self)
        db.session.commit()

    def to_json(self): 
        return {
            "id": self.id,
            "guid": self.guid,
            "category": NewCategory.query.get(self.category_id).to_json(),
            "section": NewBookSection.query.get(self.section_id).to_json()
        }

class NewCategory(db.Model): 
    __tablename__ = 'new_categories'
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    category_order = db.Column(db.Integer)
    min_age = db.Column(db.Integer)
    max_age = db.Column(db.Integer)
    books = db.relationship('NewBook', secondary=NewCategoryBook.__table__)

    @staticmethod
    def create(name, category_order, min_age, max_age): 
        if NewCategory.query.filter_by(name=name).count(): 
            return
        category_dict = dict(
            guid = str(uuid.uuid4()),
            name = name,
            category_order = category_order,
            min_age = min_age,
            max_age = max_age
        )
        new_category_obj = NewCategory(**category_dict)
        db.session.add(new_category_obj)
        db.session.commit()

    def delete(self): 
        for category_book in NewCategoryBook.query.filter_by(category_id=self.id).all(): 
            category_book.delete()
        db.session.delete(self)
        db.session.commit()

    def to_json(self): 
        return {
            "id": self.id,
            "guid": self.guid,
            "name": self.name,
            "category_order": self.category_order,
            "min_age": self.min_age,
            "max_age": self.max_age
        }

class NewBookImage(db.Model): 
    __tablename__ = 'new_book_images'
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    source = db.Column(db.String, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('new_books.id'))
    image_angle = db.Column(db.Integer, default=0)

    @staticmethod
    def create(source, book_id ,image_angle=0): 
        if NewBook.query.filter_by(id=book_id).count(): 
            book_image_dict = dict(
                guid = str(uuid.uuid4()),
                source = source,
                book_id = book_id,
                image_angle=image_angle
            )
            new_book_image_obj = NewBookImage(**book_image_dict)
            db.session.add(new_book_image_obj)
            db.session.commit()

    def delete(self): 
        db.session.delete(self)
        db.session.commit()

    def to_json(self):
     return {
        'id': self.id,
        'guid': self.guid,
        'source': self.source,
        'book_id': self.book_id,
        'image_angle': self.image_angle }

class NewBookVideo(db.Model):
    __tablename__ = 'new_videos'
    video_id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('new_books.id'))
    
    @staticmethod
    def create(source, book_id):
        if NewBook.query.filter_by(id=book_id).count() and not NewBookVideo.query.filter_by(source=source, book_id=book_id).count():
            video_dict = dict(
                source=source,
                book_id=book_id,
            )
            new_video_obj = NewBookVideo(**video_dict)
            db.session.add(new_video_obj)
            db.session.commit()
            
    def delete(self):
        db.session.delete(self)
        db.session.commit()                 
    
    def to_json(self):
        return {
            'source': self.source,
            'book_id': self.book_id,
        }
        
class NewBook(db.Model): 
    __tablename__ = 'new_books'
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    isbn = db.Column(db.String, nullable=False)
    rating = db.Column(db.String)
    review_count = db.Column(db.String)
    book_order = db.Column(db.Integer)
    min_age = db.Column(db.Integer)
    max_age = db.Column(db.Integer)
    price = db.Column(db.Float)
    for_age = db.Column(db.String)
    grade_level = db.Column(db.String)
    lexile_measure = db.Column(db.String)
    pages = db.Column(db.Integer)
    dimensions = db.Column(db.String)
    publisher = db.Column(db.String)
    publication_date = db.Column(db.Date)
    language = db.Column(db.String)
    description = db.Column(db.String)
    book_type = db.Column(db.String)
    authors = db.Column(db.String)
    genre = db.Column(db.String)
    stock_available = db.Column(db.Integer)
    rentals = db.Column(db.Integer)
    categories = db.relationship('NewCategory', secondary=NewCategoryBook.__table__)

    @staticmethod
    def create(name, image, isbn, rating, review_count, min_age, max_age, language, price): 
        if NewBook.query.filter_by(isbn=str(isbn)).count(): 
            return
        book_dict = dict(
            guid = str(uuid.uuid4()),
            name = name,
            image = image,
            isbn = isbn,
            rating = rating,
            review_count = review_count,
            min_age = min_age,
            max_age = max_age,
            language = language,
            price = price
        )
        new_book_obj = NewBook(**book_dict)
        db.session.add(new_book_obj)
        db.session.commit()

    def delete(self): 
        for category in NewCategoryBook.query.filter_by(book_id=self.id).all(): 
            category.delete()
        db.session.delete(self)
        db.session.commit()

    def to_json(self): 
        
        book = Book.query.filter_by(isbn=self.isbn).first()
        if book: 
            stock_available = book.stock_available
            rentals = book.rentals
        else:
            stock_available = self.stock_available
            rentals = self.rentals    
        return {
            "id": self.id,
            "guid": self.guid,
            "name": self.name,
            "image": self.image,
            "isbn": self.isbn,
            "rating": self.rating,
            "review_count": self.review_count,
            "book_order": self.book_order,
            "min_age": self.min_age,
            "max_age": self.max_age,
            "price": self.price,
            "for_age": self.for_age,
            "genre": self.genre,
            "lexile_measure": self.lexile_measure,
            "grade_level": self.grade_level,
            "pages": self.pages,
            "dimensions": self.dimensions,
            "publisher": self.publisher,
            "publication_date": self.publication_date,
            "language": self.language,
            "description": self.description,
            "categories": [category.to_json() for category in NewCategoryBook.query.filter_by(book_id=self.id).all()],
            "images": [image.to_json() for image in NewBookImage.query.filter_by(book_id=self.id).all()],
            "stock_available": stock_available,
            "rentals": rentals,
        }
