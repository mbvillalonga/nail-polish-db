import csv
import os
# import re
# import sys
import argparse
from models import db, Polish, SwatchPhoto, ManiPhoto, ManiLog
from app import create_app

# bash for generating list of paths of recently uploaded SWATCH photos:
    # cd static/uploads/
    # echo "path" > swatch_photo_paths_081625.csv
    # find photos/swatches -type f -name "*.jpg" -newermt "2025-08-01" -print >> swatch_photo_paths_081625.csv
    # open swatch_photo_paths_081625.csv
# then return to nail-polish-db dir and run this file with --dry-run to test

# bash for generating list of paths of MANI photos:
    # cd static/uploads/
    # echo "path" > mani_photo_paths_082425.csv
    # find photos/manis -type f -name "*.jpg" -newermt "2024-08-01" -print >> mani_photo_paths_082425.csv
    # open mani_photo_paths_082425.csv

# def extract_polish_id(filepath):
#     filename = os.path.basename(filepath)
#     parts = filename.split('_')
#     if len(parts) >= 4:
#         id_with_ext = parts[3]
#         id_clean = os.path.splitext(id_with_ext)[0]
#         return int(id_clean) if id_clean.isdigit() else None
#     return None

def parse_args():
    parser = argparse.ArgumentParser(description="Bulk import photos")
    parser.add_argument(
        "--file", "-f",         # what to allow
        default=os.getenv("IMPORT_FILENAME"),
        help="Path to the CSV file to import. If none provided, will default to .env variable IMPORT_FILENAME"
    )
    parser.add_argument(
        "--type", "-t",
        choices=["mani","polish"],
        required=True,
        help="Type of record to add (mani or polish)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",    # flag, true if present
        help="Run without committing to database"
    )

    args = parser.parse_args()
    # show for debugging
    print("File: ", args.file)
    print("Type: ", args.type)
    print("Dry run: ", args.dry_run)
    if not args.file:
        parser.error("Provide --file or set IMPORT_FILENAME in .env")

    return args

def extract_record_id(filepath, recordtype):
    

    if recordtype == 'mani':
        pathname = os.path.dirname(filepath)
        parts = pathname.split('_')
        if len(parts) >= 2:
            id_with_ext = parts[1] 
        else:
            return None
    elif recordtype == 'polish':
        filename = os.path.basename(filepath)
        parts = filename.split('_')
        if len(parts) >= 4:
            id_with_ext = parts[3]
        else:
            return None
    else:
        return None
    
    id_clean = os.path.splitext(id_with_ext)[0]
    return int(id_clean) if id_clean.isdigit() else None


# #### TESTING
# DRY_RUN = "--dry-run" in sys.argv
# if DRY_RUN:
#     print("Dry run mode: No changes will be committed to the database.")
# ####

# # Get path and filename for import from .env file
# IMPORT_FILE = os.getenv("FILENAME_IMPORT_SWATCHPIX")

def main():
    args = parse_args()

    # Create the Flask app and push the app context
    app = create_app()

    with app.app_context():
        # Import csv
        with open(args.file, newline="", encoding="utf-8-sig") as csvfile:
            # Store csv as iterable object
            reader = csv.DictReader(csvfile)

            if "path" not in (reader.fieldnames or []):
                raise ValueError("CSV must contain a 'path' column")

            # store photo paths for batch commit
            photos_to_commit = []
            unmatched_paths = []

            #### testing with only first 5 rows
            ###max_rows = 585
            ###for i, row in enumerate(reader):
            ###    if i>= max_rows:
            ###        break
            ##########

            if args.type == 'polish':
                ###print("Headers: ", reader.fieldnames) # Print column names
                # Import path from each row
                for i, row in enumerate(reader):
                    print(f"\n[{i+1}] Importing new SwatchPhoto record...")
                    photo_path = row.get("path","").strip()
                    ###print(photo_path)
                    # File root should be in format: [brand-name]_[brandID]_[polish-name-first3words]_[polishID]
                    # Additional suffixes may follow (e.g., _f, _t-c, _m-v) 
                    
                    # Extract polishID from filename
                    polish_id = extract_record_id(photo_path, args.type)
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

                if args.dry_run:
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

            elif args.type == 'mani':
                print("Headers: ", reader.fieldnames) # Print column names
                # Import path from each row
                for i, row in enumerate(reader):
                    print(f"\n[{i+1}] Importing new mani record...")
                    photo_path = row.get("path","").strip()
                    print(photo_path)
                    # Path root should be in format: YYYY-MM-DD_[mani_log_id]_[brand1abbrev]_[brand2abbrev]..._[brandnabbrev]
                    
                    # Extract mani_log_id from filename
                    mani_log_id = extract_record_id(photo_path, args.type)
                    print(f"Mani Log ID to match: {mani_log_id}")

                    if mani_log_id is not None:
                        # Find mani associated with photo
                        try:
                            mani_record = ManiLog.query.filter_by(id=int(mani_log_id)).first()
                        except ValueError:
                            print(f"Could not convert mani_log_id '{mani_log_id}' to integer.")
                            mani_record = None
                    else:
                        print("mani_log_id is None - likely due to a regex miss.")
                        mani_record = None
                    if mani_record:
                        # Add path to the mani photo (mani_photos) table
                        
                        existing_photo = ManiPhoto.query.filter_by(path=photo_path).first()

                        if existing_photo:
                            print(f"Skipping already imported photo: {photo_path}")
                        else:
                            photo = ManiPhoto(
                                path=photo_path,
                                mani_log_id=mani_record.id
                            )
                            photos_to_commit.append(photo)
                            print(f"Created new photo record to commit in batch for: Mani ID '{mani_record.id}' on {mani_record.mani_date}\n")
                        
                    if not mani_record:
                        print(f"No mani log record. Skipping import of file:\n{photo_path}")
                        unmatched_paths.append(photo_path)

                if args.dry_run:
                    print(f"\nDRY RUN: Would have imported {len(photos_to_commit)} new mani photo records.")
                else:
                    db.session.bulk_save_objects(photos_to_commit)
                    db.session.commit()
                    print(f"\nMani photo import complete! Imported {len(photos_to_commit)} new mani photo records.")
                
                if unmatched_paths:
                    print(f"\nSkipped {len(unmatched_paths)} rows due to missing mani records.")
                    print("Unmatched paths:")
                    for path in unmatched_paths:
                        print(" -", path)

if __name__ == "__main__":
    main()

