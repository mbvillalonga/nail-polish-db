import csv
import os
from models import db, app, Brand, Polish
from datetime import datetime

# Get path and filename for import from .env file
IMPORT_FILE = os.getenv("FILENAME_IMPORT_POLISHES")

with app.app_context():
    # Import csv
    with open(IMPORT_FILE, newline="", encoding="utf-8") as csvfile:
        # Store csv as iterable object
        reader = csv.DictReader(csvfile)
        #print("Headers: ", reader.fieldnames) # Print column names
        allowed_types = {"color", "top coat", "base coat", "stamping polish", "other"}

        # Import relevant information from each row
        for row in reader:
            print("Importing new polish record...")
            #print("Row: ", row) # print each row as a dictionary 

            ## ------------ Info for Brands ------------
            # Check that brand exists in Brands. If not, add it:
            brand_name = row["Brand"].strip()
            brand = Brand.query.filter_by(name=brand_name).first()

            if not brand:
                brand = Brand(name=brand_name, type="unknown")
                db.session.add(brand)
                db.session.commit() # Save the brand before using its ID
                print(f"Created new brand: {brand.name}")
            else:
                print(f"Found existing brand: {brand.name}")

            ## ------------ Info for Order Logs ------------
            # Eventually use these dates to create an Order Log if none exists already
            # Format date received field: takes string formatted as 
            # "MM/DD/YY" and reformats it using datetime.date
            date_recd = row.get("Date Received","").strip()
            date_recd = datetime.strptime(date_recd, "%m/%d/%y").date() if date_recd else None
            #print(date_recd)

            # Format order date field
            order_date = row.get("Order Date","").strip()
            order_date = datetime.strptime(order_date, "%m/%d/%y").date() if order_date else None
            # REFORMAT AS YYYY-MM-DD to match with order_log
            #print(order_date)
            
            ## ------------ Info for Polishes ------------
            polish_name = row["\ufeffName"].strip()
            polish = Polish.query.filter_by(name=polish_name, brand_id=brand.id).first()

            # check if polish name exists yet, for that specific brand 
            # (in case different brands have the same polish name)
            # if polish record does not exist, create it
            # using get() helps prevent errors if a column is missing
            if not polish:
                # make sure polish_type is formatted correctly
                polish_type = row.get("Type", "").strip().lower()

                if polish_type not in allowed_types: # convert invalid values to "color" 
                    print(f"Invalid polish type '{polish_type}', defaulting to 'color'")
                    polish_type = "color"

                polish = Polish(
                    name=polish_name,
                    polish_type=polish_type,
                    color_family=row.get("Swatch ring","").strip(),
                    full_desc=row.get("Full Description","").strip(),
                    tags=row.get("Tags","").strip(),
                    brand_id=brand.id,
                )

                db.session.add(polish)
                db.session.commit() # Save the brand before using its ID
                print(f"Created new polish record: {polish.name} by {brand.name}\n")

            else:
                print(f"Found existing polish record: {polish.name} by {brand.name}\n")
