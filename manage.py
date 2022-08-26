from flask.cli import FlaskGroup
from app import create_app, db
from flask import current_app

from seed_4 import *
from export import *
from seed_users import *
from script_order import *
from scripts.script_25_aug import *
from scripts.script_26_aug import *

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
def export_db():
    export()

@cli.command()
def seed_users_data():
    seed_users()

@cli.command()
def script_create_orders():
    create_orders()

@cli.command()
def script_25_aug():
    add_books()
    aug_25()
    # populate_suggestions()

@cli.command()
def script_26_aug():
    aug_26_1()

if __name__ == '__main__':
    cli()