import csv
import pandas as pd
import os
from models import db, app, OrderLog, Polish, Brand
from datetime import datetime

# Get path and filename for import from .env
IMPORT_FILE = os.getenv("FILENAME_IMPORT_ORDERS")

# Import xlsx
order_df = pd.read_excel(IMPORT_FILE, engine="openpyxl", dtype="str").fillna("")
order_data = order_df.to_dict(orient="records") # converts dataframe to list of dicts

with app.app_context():
    # Ensure that brand Unknown exists
    brand = Brand.query.filter_by(name="Unknown").first()
    if not brand:
        brand = Brand(name="Unknown")
        db.session.add(brand)
        db.session.commit()
        print("Added fallback brand: Unknown")
    else:
        print("Unknown brand already exists. OK to continue with Order Log import.\n")

    for rec in order_data:
        # Extract data from .xslx
        order_desc = rec["Order Description"].strip()
        order_date_str = rec["Date"].strip()
        order_date_recd_str = rec["Date Received"].strip()
        order_total = float(rec["Total Paid"].replace("$", "").strip()) if rec["Total Paid"] else 0.0
        subtot_polish = float(rec["Polish Total"].replace("$", "").strip()) if rec["Polish Total"] else 0.0
        subtot_other = float(rec["Other Total"].replace("$", "").strip()) if rec["Other Total"] else 0.0
        subtot_shiptax = float(rec["Shipping & Tax"].replace("$", "").strip()) if rec["Shipping & Tax"] else 0.0
        subtot_discount = float(rec["Total paid with gift card"].replace("$", "").strip()) if rec["Total paid with gift card"] else 0.0
        polish_names_raw = rec["Polish Collection copy"].strip()
        brand_tags = rec["Tags"].strip().split(",")

        print(order_desc)
        print(order_date_str)
        print(order_total)
        print(subtot_polish)
        print(subtot_other)
        print(subtot_shiptax)
        print(subtot_discount)
        print(polish_names_raw)
        print(brand_tags)
    # N/A   ->  subtotal_ingredient 

        # Step 2: Insert order into OrderLog table
        # Reformat date variables
        order_date = datetime.strptime(order_date_str, "%Y-%m-%d %H:%M:%S").date() if order_date_str else None
            #order_date_recd = datetime.strptime(order_date_recd_str, "%m/%d/%y").date() if order_date_recd_str else None
            # TO ADD LATER: NEED TO ADD ORDER_RECD TO MODELS
        #order_date = datetime.strftime("%Y-%m-%d") if order_date_str else None
        print(order_date)
        # Check if order_desc exists in OrderLog on that date
        order = OrderLog.query.filter_by(order_date=order_date, vendor=order_desc).first()

        # If it does NOT exist, create a new OrderLog entry.
        if not order:
            order = OrderLog(order_date=order_date, vendor=order_desc, order_total=order_total)
            db.session.add(order)
            print(f"Created new order: {order_desc} on {order_date}")

    # Step 3: Create polish entries (if not already in database)
        if polish_names_raw:
            polish_names = list(csv.reader([polish_names_raw], skipinitialspace=True))[0]
            polish_names = [name.strip() for name in polish_names]
            print(polish_names)

            # For each name in "Polish Collection copy", check if it exists in Polish.
            existing_polishes = {p.name: p for p in Polish.query.filter(Polish.name.in_(polish_names)).all()}
            #existing_brands = {b.name: b for b in Brand.query.all()}
            brand = Brand.query.filter_by(name="Unknown").first()

            for polish_name in polish_names:
                polish = existing_polishes.get(polish_name)
            
            # (TO ADD LATER, MAYBE) If it exists, make sure it's linked with the correct brand
            # Attempt to determine the correct brand for the new polish using the Tags column

                # If it does NOT exist, create a new Polish entry
                if not polish:
                    polish = Polish(name=polish_name, brand_id=brand.id)
                    db.session.add(polish)
                    existing_polishes[polish_name] = polish
                    print(f"Created new polish record: '{polish_name}'")

                # Link polish to order
                if polish not in order.polish:
                    order.polish.append(polish)  # many-to-many 
                    print(f"Linked {polish.name} to order {order.vendor}")     

        db.session.commit() # Save all changes