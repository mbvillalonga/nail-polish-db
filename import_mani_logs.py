import csv
import os
import re
from models import db, ManiLog, Polish, ManiPhoto
from datetime import datetime
from app import create_app

# Get path and filename for import from .env file
IMPORT_FILE = os.getenv("FILENAME_IMPORT_MANIS")

# Create the Flask app and push the app context
app = create_app()

def smart_split(csv_string):
    return next(csv.reader([csv_string], skipinitialspace=True))

with app.app_context():

    new_mani_count = 0
    new_photo_count = 0
    polishes_linked = 0
    skipped_polishes = []

    # Import csv
    with open(IMPORT_FILE, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # Skip empty rows
            if not any(cell.strip() for cell in row.values()):
                continue
            mani_name = row.get("Name","").strip() # Add this in later with text formatting steps

            mani_date_str = row.get("Date","").strip()
            mani_date = datetime.strptime(mani_date_str, "%m/%d/%y").date() if mani_date_str else None
            # add reformatting of date so that it is yyyy-mm-dd

            tags = row.get("Tags","").strip() # Need to add to model

            mani_polishes_raw = row.get("Polish(es) used","").strip() # Cleans imported text
            mani_polishes = {name.strip() for name in smart_split(mani_polishes_raw)} # Cleans imported text
            
            photo_paths_raw = row.get("Pic","").strip() # Cleans imported text
            photo_paths = [re.sub(r'\([^)]*\)', '', s).strip() for s in smart_split(photo_paths_raw)] # Cleans imported text
            
            mani_notes = row.get("Notes","").strip()

            # Check if any mani entries already exist for that date
            mani_logs_on_date = ManiLog.query.filter_by(mani_date=mani_date).all()
            
            # Check if any existing mani entry has the exact same polishes (order does not matter)
            match_found = False
            for existing_mani in mani_logs_on_date:
                existing_polish_names = {p.name for p in existing_mani.polish}
                # check if this will work independent of ordering of polishes
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
                new_mani_count += 1
            
            # Link mani_polishes to polishes
            for polish_name in mani_polishes:
                polish = Polish.query.filter_by(name=polish_name).first()
                if polish:
                    if polish not in mani_log.polish:
                        mani_log.polish.append(polish)
                        polishes_linked += 1
                        print(f"Linked '{polish.name}' to manicure on {mani_date}")
                else:
                    skipped_polishes.append(polish_name)
                    print(f"WARNING: Polish '{polish_name}' not found. Skipping.")
        
            # # Link paths to mani_photos
            # for path in photo_paths:
            #     if not path:
            #         continue
            #     existing_photo = ManiPhoto.query.filter_by(path=path, mani_log_id=mani_log.id).first()
            #     if not existing_photo:
            #         mani_photo = ManiPhoto(path=path, mani_log_id=mani_log.id)
            #         db.session.add(mani_photo)
            #         new_photo_count += 1
            #         print(f"Added mani photo for {mani_date}: {path}")

        db.session.commit()
            
    # Summary
    print("\nImport complete!")
    print(f"New mani logs: {new_mani_count}")
    print(f"Polishes linked: {polishes_linked}")
    # print(f"New photos added: {new_photo_count}")
    if skipped_polishes:
        print(f"Polishes not found ({len(skipped_polishes)}): {set(skipped_polishes)}")
