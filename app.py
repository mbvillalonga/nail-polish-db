from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from models import db, migrate, Polish, Brand, Tag, ManiLog
from dotenv import load_dotenv
from sqlalchemy import func
from datetime import datetime
import os
import json

"""
app.py
Set up routes for nail-polish-db: display polish inventory, display mani logs, and add new records.
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
    
    # Route for adding a new polish record
    @app.route("/polishes/add", methods=["GET", "POST"])
    def add_polish():
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
            "add_polish.html", 
            brands=brands,
            color_family_labels = color_family_labels,
            polish_type_labels = polish_type_labels
        )  # displays the add_polish.html form
    
    # Route for handling in-line updates
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
    
    # Route for updating tags in-line
    @app.route("/update_polish_tags", methods=["POST"])
    def update_polish_tags():
        data = request.get_json()
        polish_id = data.get("id")
        tag_names = data.get("tags", [])

        polish = Polish.query.get(polish_id)
        if not polish:
            return jsonify({"success": False, "error": "Polish not found"}), 404
        
        # store current tags before update
        previous_tags = set(polish.tag)

        # normalize tags to lowercase
        # tag_names = list(set(t.strip().lower() for t in tag_names if t.strip()))

        # create / fetch new tags
        new_tags = []

        for name in tag_names:
            tag = None
            name = name.strip()

            if name.isdigit():
                # try looking up tag by ID if this is a digit
                tag = Tag.query.filter_by(id=int(name)).first()

            if not tag:
                # fall back to treating it as a name (normalize to lowercase)
                tag = Tag.query.filter_by(name=name.lower()).first()

            if not tag:
                # create new tag if it doesn't exist yet
                tag = Tag(name=name.lower())
                db.session.add(tag)
                
            new_tags.append(tag)
        
        # update
        polish.tag = new_tags
        db.session.commit()

        # # identify and delete orphaned tags
        # removed_tags = previous_tags - set(new_tags)
        # for tag in removed_tags:
        #    if not tag.polish: # no other polish uses this tag
        #        db.session.delete(tag)
        # db.session.commit()

        return jsonify({"success": True})

    # Route for displaying mani logs
    @app.route("/manis")
    def view_mani_logs():
        mani_logs = ManiLog.query.order_by(ManiLog.mani_date.desc()).all()
        return render_template("mani_logs.html", mani_logs=mani_logs)

    # Route for adding new mani log
    @app.route("/manis/add", methods=["GET", "POST"])
    def add_mani():

        if request.method == "POST":  # when user submits the form:
            # extract date from form 
            date_str = request.form["date"]
            mani_date = datetime.strptime(date_str, "%Y-%m-%d").date() 

            # extract polishes used from form       
            polish_ids = request.form.getlist("polishes_used")     
            polishes_used = (
                Polish.query.filter(Polish.id.in_(polish_ids)).all()
                if polish_ids else []
            )

            # extract tags from form 
            tag_ids = request.form.getlist("tags")
            tags = []
            for tag_id in tag_ids:
                tag = Tag.query.get(tag_id) # check if this tag already exists in the Tag table
                # if not tag: # if it doesn't exist yet
                    # tag = Tag(name=tag_name) # stage a new record in Tag table
                    # db.session.add(tag) # add new Tag record
                if tag:
                    tags.append(tag)# add existing Tag name to mani_logs.tags
                
            # check if a ManiLog record exists for this date already 
            existing = ManiLog.query.filter_by(mani_date=mani_date).first()

            if not existing:
                new_mani = ManiLog( # create new ManiLog record
                    mani_date=mani_date, 
                    polish=polishes_used,
                    tag=tags
                )  
                db.session.add(new_mani)  # save to ManiLogs table
                db.session.commit()
                flash(f"Manicure Log added for {new_mani.mani_date}", "success")
            #else: # add logic here so that I check whether the mani record on that date includes the same polishes; 
                #if not, log a new ManiLog on the same date (different ID)

            return redirect(url_for("view_mani_logs"))  # return to list of mani logs 
        
        return render_template("add_mani.html")  # displays the add_mani.html form

    # Route for updating mani log records in-line
    @app.route("/update_mani_record", methods=["POST"])
    def update_polish_record():
        data = request.get_json()
        mani_log_id = data.get("id")
        field = data.get("field")
        value = data.get("value")

        mani = ManiLog.query.get(mani_log_id)
        if not mani:
            return jsonify({'success': False, 'error': 'Mani record not found'}), 404

        if field not in {"mani_date", "polish", "tag"}:
            return jsonify({"success": False, 'error': 'Field not editable'}), 400
        
        if field == "mani_date":
            from datetime import datetime
            try:
                value = datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid date format'}), 400
            
        setattr(mani, field, value)
        db.session.commit()

        return jsonify({"success": True})

    # Search route for polishes
    @app.route("/search/polishes")
    def search_polishes():
        query = request.args.get("q", "").strip().lower()

        results = (
            db.session.query(Polish.id, Polish.name, Brand.name)
            .join(Brand)
            .filter(Polish.name.ilike(f"%{query}%"))
            .limit(10)
            .all()
        )

        return jsonify([
            {
                "value": str(pid),
                "label": f"{pname} ({bname})"
            }
            for pid, pname, bname in results
        ])

    # Search route for tags
    @app.route("/search/tags")
    def search_tags():
        query = request.args.get("q", "").strip().lower()
        if not query:
            return jsonify([])

        results = (
            db.session.query(Tag.id, Tag.name)
            .filter(Tag.name.ilike(f"%{query}%"))
            .order_by(Tag.name)
            .limit(10)
            .all()
        )
        return jsonify([
            {
                "value": str(tid),
                "label": f"{tname}"
            }
            for tid, tname in results])
    
    # Route for accessing my data
    @app.route("/my_data/<path:filename>")
    def serve_my_data(filename):
        return send_from_directory("my_data", filename)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)  # starts the Flask development server for testing