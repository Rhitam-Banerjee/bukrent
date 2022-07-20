from flask.cli import FlaskGroup
from app import create_app, db
from flask import current_app

# from seed import *
from seed_final import *
from export import *

from app.models.annotations import Annotation
from app.models.author import Author
from app.models.books import Book
from app.models.category import Category
from app.models.details import Detail
from app.models.publishers import Publisher
from app.models.reviews import Review
from app.models.series import Series

app = create_app()
cli = FlaskGroup(create_app=create_app)

@cli.command()
def recreate_db():
    if current_app.config.get('ENV') not in ('development', 'test', 'testing'):
       print("ERROR: recreate-db only allowed in development and testing env.")
       return
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command()
def seed_db():
    seed()

@cli.command()
def export():
    export()

if __name__ == '__main__':
    cli()