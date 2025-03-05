import csv
import os
import re
from models import db, app, ManiLog, Polish, ManiPhoto
from datetime import datetime

# Get path and filename for import from .env file
IMPORT_FILE = os.getenv("FILENAME_IMPORT_MANIS")

with app.app_context():
    # Import csv
    with open(IMPORT_FILE, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # mani_name = row.get("Name","").strip() # Add this in later with text formatting steps
            mani_date_str = row.get("Date","").strip()
            mani_date = datetime.strptime(mani_date_str, "%m/%d/%y").date() if mani_date_str else None
            mani_tags = row.get("Tags","").strip() # Need to add to model
            mani_polishes_raw = row.get("Polish(es) used","").strip().split(",") # Cleans imported text
            mani_polishes = {polish_name.strip() for polish_name in mani_polishes_raw} # Cleans imported text
            mani_photo_path_raw = row.get("Pic","").strip().split(",") # Cleans imported text
            mani_photo_path = [re.sub(r'\([^)]*\)', '', s).strip() for s in mani_photo_path_raw] # Cleans imported text
            mani_notes = row.get("Notes","").strip()

            # Check if any mani entries already exist for that date
            mani_logs_on_date = ManiLog.query.filter_by(mani_date=mani_date).all()
            
            # Check if any existing mani entry has the exact same polishes (order does not matter)
            match_found = False
            for existing_mani in mani_logs_on_date:
                existing_polish_names = {polish.name for polish in existing_mani.polish}

                if mani_polishes == existing_polish_names:
                    print(f"Manicure log already exists for {mani_date} with same polish(es):\n{mani_polishes}")
                    match_found = True
                    mani_log = existing_mani
                    break
            
            if not match_found: # If no entry exists for that date with the same polishes:
                mani_log = ManiLog(mani_date=mani_date)
                db.session.add(mani_log)
                db.session.commit()
                print(f"Added new manicure log for {mani_date} with polish(es):\n{mani_polishes}")
            
            # Link mani_polishes to polishes
            for polish_name in mani_polishes:
                polish = Polish.query.filter_by(name=polish_name).first()
                if polish:
                    if polish not in mani_log.polish:
                        mani_log.polish.append(polish)
                        print(f"Linked '{polish.name}' to manicure on {mani_date}")
                else:
                    print(f"WARNING: Polish '{polish_name}' not found. Skipping.")
        
            # Link paths to mani_photos
            for photo_path in mani_photo_path:
                existing_photo = ManiPhoto.query.filter_by(path=photo_path, mani_log_id=mani_log.id).first()
                if not existing_photo:
                    mani_photo = ManiPhoto(path=photo_path, mani_log_id=mani_log.id)
                    db.session.add(mani_photo)
                    print(f"Added mani photo for {mani_date}: {photo_path}")

            db.session.commit()
            