import csv
import os
import re
import sys
from models import db, Polish, SwatchPhoto
from app import create_app

def extract_polish_id(filepath):
    filename = os.path.basename(filepath)
    parts = filename.split('_')
    if len(parts) >= 4:
        id_with_ext = parts[3]
        id_clean = os.path.splitext(id_with_ext)[0]
        return int(id_clean) if id_clean.isdigit() else None
    return None

#### TESTING
DRY_RUN = "--dry-run" in sys.argv
if DRY_RUN:
    print("Dry run mode: No changes will be committed to the database.")
####

# Get path and filename for import from .env file
IMPORT_FILE = os.getenv("FILENAME_IMPORT_SWATCHPIX")

# Create the Flask app and push the app context
app = create_app()

with app.app_context():
    # Import csv
    with open(IMPORT_FILE, newline="", encoding="utf-8-sig") as csvfile:
        # Store csv as iterable object
        reader = csv.DictReader(csvfile)

        # store photo paths for batch commit
        photos_to_commit = []
        unmatched_paths = []

        #### testing with only first 5 rows
        ###max_rows = 585
        ###for i, row in enumerate(reader):
        ###    if i>= max_rows:
        ###        break
        ##########

        # Import path from each row
        for i, row in enumerate(reader):
            print(f"\n[{i+1}] Importing new SwatchPhoto record...")
            ###print("Headers: ", reader.fieldnames) # Print column names
            photo_path = row.get("path","").strip()
            ###print(photo_path)
            # File root should be in format: [brand-name]_[brandID]_[polish-name-first3words]_[polishID]
            # Additional suffixes may follow (e.g., _f, _t-c, _m-v) 
            
            # Extract polishID from filename
            polish_id = extract_polish_id(photo_path)
            print(f"Polish ID to match: {polish_id}")

            if polish_id is not None:
                # Find polish associated with photo
                try:
                    polish_record = Polish.query.filter_by(id=int(polish_id)).first()
                except ValueError:
                    print(f"Could not convert polish_id '{polish_id}' to integer.")
                    polish_record = None
            else:
                print("polish_id is None - likely due to a regex miss.")
                polish_record = None
            if polish_record:
                # Add path to the SwatchPhoto (swatch_photos) table
                
                existing_photo = SwatchPhoto.query.filter_by(path=photo_path).first()

                if existing_photo:
                    print(f"Skipping already imported photo: {photo_path}")
                else:
                    photo = SwatchPhoto(
                        path=photo_path,
                        polish_id=polish_record.id
                    )
                    photos_to_commit.append(photo)
                    print(f"Created new photo record to commit in batch for: '{polish_record.name}' by {polish_record.brand.name}\n")
                
            if not polish_record:
                print(f"No polish record. Skipping import of file:\n{photo_path}")
                unmatched_paths.append(photo_path)

        if DRY_RUN:
            print(f"\nDRY RUN: Would have imported {len(photos_to_commit)} new swatch photo records.")
        else:
            db.session.bulk_save_objects(photos_to_commit)
            db.session.commit()
            print(f"\nSwatch photo import complete! Imported {len(photos_to_commit)} new photo records.")
        
        if unmatched_paths:
            print(f"\nSkipped {len(unmatched_paths)} rows due to missing polish records.")
            print("Unmatched paths:")
            for path in unmatched_paths:
                print(" -", path)
 


