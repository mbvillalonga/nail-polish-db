from flask import Flask, render_template, request, redirect, url_for, flash
#from flask_migrate import Migrate
#from flask_sqlalchemy import SQLAlchemy
from models import db, migrate, Polish, Brand
from dotenv import load_dotenv
import os

"""
app.py
Set up a basic route to display polish inventory and add new records.
Mercedes Villalonga, 2025
"""

# load env variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "dev")  # for session + flash support

    # Configure DB
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # Home route for displaying all polishes
    @app.route("/")
    def index():
        polishes = Polish.query.all()  # retrieve all polishes stored in the Polish table
        return render_template(
            "index.html", polishes=polishes
        )  # render index.html template


    # Route for adding a new polish record
    @app.route("/add", methods=["GET", "POST"])
    def add():
        brands = Brand.query.order_by(Brand.name).all()

        if request.method == "POST":  # when user submits the form:
            name = request.form["name"].strip()  # extract name
            selected_brand = request.form["brand"]
            new_brand_input = request.form.get("new_brand", "").strip()
    #        brand_name = request.form["brand"]  # extract brand
            color_family = request.form["color_family"].strip() # extract color
            full_desc = request.form.get("full_desc", "").strip() # extract description
            polish_type = request.form["polish_type"]
            tags = request.form.get("tags","").strip()

            # select brand
            if selected_brand == "new" and new_brand_input:
                brand = Brand.query.filter_by(name=new_brand_input).first()
                if not brand:
                    brand = Brand(name=new_brand_input, type="unknown")
                    db.session.add(brand)
                    db.session.commit()
            else:
                brand = Brand.query.filter_by(id=int(selected_brand)).first()
            
            # check if polish exists for this brand 
            existing = Polish.query.filter_by(name=name, brand_id=brand.id).first()
            if not existing:
                new_polish = Polish( # create new record
                    name=name, 
                    polish_type=polish_type,
                    brand_id=brand.id, 
                    color_family=color_family, 
                    full_desc=full_desc,
                    tags=tags
                )  
                db.session.add(new_polish)  # save to table
                db.session.commit()
                flash(f"Added polish: {new_polish.name} by {brand.name}", "success")
            return redirect(url_for("index"))  # return to home page
        return render_template("add.html", brands=brands)  # displays the add.html form

    # Route for displaying all polishes and info: brand, color, etc.
    @app.route("/polishes")
    def view_polishes():
        polishes = Polish.query.order_by(Polish.name).all()
        return render_template("polishes.html", polishes=polishes)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)  # starts the Flask development server for testing
