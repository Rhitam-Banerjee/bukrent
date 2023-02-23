from app.models.new_books import NewBookImage, NewBook

def seed_multiple_images(): 
    books = NewBook.query.all()
    for i in range(len(books)): 
        NewBookImage.create(books[i].image, books[i].id)
        print(f'{i + 1} / {len(books)}')