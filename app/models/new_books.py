from app import db
import uuid

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
            guid = str(uuid.uuid4()),
            name = name
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
                guid = str(uuid.uuid4()),
                category_id = category_id,
                book_id = book_id,
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

    categories = db.relationship('NewCategory', secondary=NewCategoryBook.__table__)

    @staticmethod
    def create(name, image, isbn, rating, review_count, book_order, min_age, max_age):
        book_dict = dict(
            guid = str(uuid.uuid4()),
            name = name,
            image = image,
            isbn = isbn,
            rating = rating,
            review_count = review_count,
            book_order = book_order,
            min_age = min_age,
            max_age = max_age
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
            "categories": [category.to_json() for category in NewCategoryBook.query.filter_by(book_id=self.id).all()],
        }