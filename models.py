import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# pass subclass of DeclarativeBase
class Base(DeclarativeBase):
    pass

# create the db object 
db = SQLAlchemy(model_class=Base)

# initialize a new Flask web app
app = Flask(__name__) 

# load env variables
load_dotenv()

# retrieve database credentials from .env file
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

# connect Flask to MySQL and disable object modification tracking
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db) # enable flask-migrate

# Brands table (basics, no relationships)
class Brands(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(75))
    type = db.Column(db.Enum('indie','boutique','mainstream','luxury','unknown', 
                            name='brand_types', 
                            nullable=False,
                            default='unknown'))
    # eventually add:
    # website url (string with link)
    # num_owned (relationship with Polish, sum of owned)
    # num_destashed (relationship with Polish, sum of destashed)

# Polish table (basics, no relationships)
class Polish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    brand = db.Column(db.String(75))
    color = db.Column(db.String(50))
    full_desc = db.Column(db.String(400))
    # eventually add:
    # color_group (single-select)
    # tags (multi-select describing finishes, pigment types, formula, etc.)
    # swatch_photo (path for displaying in GUI app)
    # mani_photos (path for displaying in GUI app)
    # usage_amt (calculated from ManicureLog)
    # destash_flag (single-select, can remain blank)

# OrderLog table (basics, no relationships)
class OrderLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime)
    order_total = db.Column(db.Float)
    # eventually add:
    # polishes_bought (one-to-many relationship with Polish)
    # ingredients_bought (FK; one-to-many relationship with IngredientLib)
    # num_polishes (number of polishes in polishes_bought)
    # subtotal_polish (float)
    # subtotal_ingredient (float)
    # subtotal_other (float)
    # subtotal_ship_tax (float)
    # subtotal_discount (float)
    # total_spent (float)
    # cost_per_polish (float)

# ManicureLog table (basics, no relationships)
class ManicureLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mani_date = db.Column(db.DateTime)
    # eventually add:
    # polishes_used (one-to-many relationship with Polish)
    # tags (multi-select, will be used to calculate usage stats)
    # mani_photos (path for displaying in GUI app)


# IngredientLib table (basics, no relationships)
class IngredientLib(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    vendor = db.Column(db.String(150), nullable=False)
    # eventually add:
    # tags
    # qty_vol
    # qty_weight
    # particle_size
    # order_date (relationship with OrderLog)
    # recipes (relationship with RecipeLog)

# RecipeLog table (basics, no relationships)
class RecipeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    # eventually add:
    # ingredients
    # qty (of each ingredient)
    # notes

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

