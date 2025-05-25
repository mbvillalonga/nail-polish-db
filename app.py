from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from models import db, migrate, Polish, Brand, Tag, ManiLog
from dotenv import load_dotenv
from sqlalchemy import func
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

    # Home route for landing page
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

        # Color family labels
        color_family_labels = {
            "clear/white": "Clear / White",
            "black": "Black",
            "grey/silver": "Grey / Silver",
            "nude/gold/brown": "Nude / Gold / Brown",
            "red": "Red",
            "coral/orange": "Coral / Orange",
            "yellow": "Yellow",
            "green": "Green",
            "teal/turq/aqua": "Teal / Turquoise / Aqua",
            "blue": "Blue",
            "indigo": "Indigo",
            "violet": "Violet",
            "fuchsia": "Fuchsia",
            "pink": "Pink",
            "base/top coat": "Base / Top Coat"
        }

        polish_type_labels = {
            "color": "Color",
            "top coat": "Top Coat",
            "base coat": "Base Coat",
            "stamping polish": "Stamping Polish",
            "other": "Other"
        }

        if request.method == "POST":  # when user submits the form:
            name = request.form["name"].strip()  # extract polish name

            # brand
            selected_brand = request.form["brand"]
            new_brand_input = request.form.get("new_brand", "").strip()

            if selected_brand == "new" and new_brand_input:
                brand = Brand.query.filter_by(name=new_brand_input).first()
                if not brand:
                    brand = Brand(name=new_brand_input, type="unknown")
                    db.session.add(brand)
                    db.session.commit()
            else:
                brand = Brand.query.filter_by(id=int(selected_brand)).first()

            if not brand:
                flash("Brand could not be determined.", "error")
                return redirect(url_for("add_polish"))

            color_family = request.form.get("color_family") # extract color
            if color_family == "":
                color_family = None

            full_desc = request.form.get("full_desc", "").strip() # extract description

            polish_type = request.form["polish_type"] # extract polish type

            # extract tags
            tag_names = request.form.get("tags", "").split(",")
            tag_names = [t.strip().lower() for t in tag_names if t.strip()] #
            tags = []

            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                tags.append(tag)

            # check if polish exists for this brand 
            existing = Polish.query.filter_by(name=name, brand_id=brand.id).first()

            if not existing:
                new_polish = Polish( # create new record
                    name=name, 
                    polish_type=polish_type,
                    brand_id=brand.id, 
                    color_family=color_family, 
                    full_desc=full_desc,
                    tag=tags
                )  
                db.session.add(new_polish)  # save to table
                db.session.commit()
                flash(f"Polish added: {new_polish.name} by {brand.name}", "success")

            return redirect(url_for("index"))  # return to home page
        
        return render_template(
            "add.html", 
            brands=brands,
            color_family_labels = color_family_labels,
            polish_type_labels = polish_type_labels
        )  # displays the add.html form

    # Route for displaying all polishes and info: brand, color, etc.
    @app.route("/polishes")
    def view_polishes():
        #polishes = Polish.query.order_by(Polish.name).all()
        #return render_template("polishes.html", polishes=polishes)
    
        polishes_query = Polish.query

        # Get filter parameters
        brand_ids = request.args.getlist("brand_id")
        colors = request.args.getlist("color_family")
        types = request.args.getlist("polish_type")
        tag_ids = request.args.getlist("tag")
        tag_logic = request.args.get("tag_logic", "or")
        destashed_only = request.args.get("destashed")

        # Apply filters dynamically
        if brand_ids:
            polishes_query = polishes_query.filter(Polish.brand_id.in_(brand_ids))

        if colors:
            polishes_query = polishes_query.filter(Polish.color_family.in_(colors))

        if types:
            polishes_query = polishes_query.filter(Polish.polish_type.in_(types))

        if destashed_only:
            polishes_query = polishes_query.filter_by(destashed_flag=True)

        if tag_ids:
            tag_ids = [int(tid) for tid in tag_ids]

            if tag_logic == "and":
                for tag_id in tag_ids:
                    polishes_query = polishes_query.filter(Polish.tag.any(Tag.id == tag_id))
            else:
                polishes_query = polishes_query.filter(Polish.tag.any(Tag.id.in_(tag_ids)))

        polishes = polishes_query.order_by(Polish.name).all()

        # Pass data needed for filter form dropdowns
        all_brands = Brand.query.order_by(Brand.name).all()
        brand_names = [b.name for b in Brand.query.order_by(Brand.name).all()]

        all_tags = Tag.query.order_by(Tag.name).all()

        color_families = list(Polish.color_family.property.columns[0].type.enums)
        color_families_options = Polish.color_family.property.columns[0].type.enums

        polish_types = list(Polish.polish_type.property.columns[0].type.enums)

        return render_template(
            "polishes.html",
            polishes=polishes,
            all_brands=all_brands,
            brand_names=brand_names,
            all_tags=all_tags,
            color_families=color_families,
            color_families_options=color_families_options,
            polish_types=polish_types,
            request=request,
        )
    
    # route for handling in-line updates
    @app.route("/update_polish_field", methods=["POST"])
    def update_polish_field():
        data = request.get_json()
        polish_id = data.get("id")
        field = data.get("field")
        value = data.get("value")

        polish = Polish.query.get(polish_id)

        if field == "brand":
            brand = Brand.query.filter(func.lower(Brand.name) == value.strip().lower()).first()            
            if not brand:
                return jsonify({"success": False, "error": "Brand not found"}), 400
                #add new brand: POTENTIALLY, LATER:
                # brand = Brand(name=value.strip())
                # db.session.add(brand) 
                # db.session.flush() #get brand.id without committing
            polish.brand_id = brand.id
        else:
            setattr(polish, field, value.strip())

        if not polish or field not in {"name", "full_desc", "color_family", "brand"}:
            return jsonify({"success": False}), 400
        
        db.session.commit()
        return jsonify({"success": True})
    
    # Route for displaying mani logs
    @app.route("/manis")
    def view_mani_logs():
        mani_logs = ManiLog.query.order_by(ManiLog.mani_date.desc()).all()
        return render_template("mani_logs.html", mani_logs=mani_logs)

    # # Route for adding new mani log
    # # Route for adding a new polish record
    # @app.route("/manis/add", methods=["GET", "POST"])
    # def add():
    #     brands = Brand.query.order_by(Brand.name).all()

    #     # Color family labels
    #     color_family_labels = {
    #         "clear/white": "Clear / White",
    #         "black": "Black",
    #         "grey/silver": "Grey / Silver",
    #         "nude/gold/brown": "Nude / Gold / Brown",
    #         "red": "Red",
    #         "coral/orange": "Coral / Orange",
    #         "yellow": "Yellow",
    #         "green": "Green",
    #         "teal/turq/aqua": "Teal / Turquoise / Aqua",
    #         "blue": "Blue",
    #         "indigo": "Indigo",
    #         "violet": "Violet",
    #         "fuchsia": "Fuchsia",
    #         "pink": "Pink",
    #         "base/top coat": "Base / Top Coat"
    #     }

    #     polish_type_labels = {
    #         "color": "Color",
    #         "top coat": "Top Coat",
    #         "base coat": "Base Coat",
    #         "stamping polish": "Stamping Polish",
    #         "other": "Other"
    #     }

    #     if request.method == "POST":  # when user submits the form:
    #         name = request.form["name"].strip()  # extract polish name

    #         # brand
    #         selected_brand = request.form["brand"]
    #         new_brand_input = request.form.get("new_brand", "").strip()

    #         if selected_brand == "new" and new_brand_input:
    #             brand = Brand.query.filter_by(name=new_brand_input).first()
    #             if not brand:
    #                 brand = Brand(name=new_brand_input, type="unknown")
    #                 db.session.add(brand)
    #                 db.session.commit()
    #         else:
    #             brand = Brand.query.filter_by(id=int(selected_brand)).first()

    #         if not brand:
    #             flash("Brand could not be determined.", "error")
    #             return redirect(url_for("add_polish"))

    #         color_family = request.form.get("color_family") # extract color
    #         if color_family == "":
    #             color_family = None

    #         full_desc = request.form.get("full_desc", "").strip() # extract description

    #         polish_type = request.form["polish_type"] # extract polish type

    #         # extract tags
    #         tag_names = request.form.get("tags", "").split(",")
    #         tag_names = [t.strip().lower() for t in tag_names if t.strip()] #
    #         tags = []

    #         for tag_name in tag_names:
    #             tag = Tag.query.filter_by(name=tag_name).first()
    #             if not tag:
    #                 tag = Tag(name=tag_name)
    #                 db.session.add(tag)
    #             tags.append(tag)

    #         # check if polish exists for this brand 
    #         existing = Polish.query.filter_by(name=name, brand_id=brand.id).first()

    #         if not existing:
    #             new_polish = Polish( # create new record
    #                 name=name, 
    #                 polish_type=polish_type,
    #                 brand_id=brand.id, 
    #                 color_family=color_family, 
    #                 full_desc=full_desc,
    #                 tag=tags
    #             )  
    #             db.session.add(new_polish)  # save to table
    #             db.session.commit()
    #             flash(f"Polish added: {new_polish.name} by {brand.name}", "success")

    #         return redirect(url_for("index"))  # return to home page
        
    #     return render_template(
    #         "add.html", 
    #         brands=brands,
    #         color_family_labels = color_family_labels,
    #         polish_type_labels = polish_type_labels
    #     )  # displays the add.html form

    # Route for accessing my data
    @app.route("/my_data/<path:filename>")
    def serve_my_data(filename):
        return send_from_directory("my_data", filename)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)  # starts the Flask development server for testing