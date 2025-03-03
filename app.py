# app.py
# Set up a basic route to display polish inventory and add new records.

from flask import Flask,render_template, request, redirect, url_for
from models import db, Polish, app


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
    if request.method == "POST":  # when user submits the form:
        name = request.form["name"]  # extract name, brand, color,
        brand = request.form["brand"]  # and full_desc fields from form
        color = request.form["color"]
        full_desc = request.form["full_desc"]

        new_polish = Polish(
            name=name, brand=brand, color=color, full_desc=full_desc
        )  # create new record
        db.session.add(new_polish)  # save to table
        db.session.commit()

        return redirect(url_for("index"))  # return to home page

    return render_template("add.html")  # displays the add.html form


if __name__ == "__main__":
    app.run(debug=True)  # starts the Flask development server for testing
