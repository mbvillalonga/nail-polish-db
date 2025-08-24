# nail-polish-db

*An interactive web application for managing inventory, product photos, and usage logs in a structured relational database. Built with Python, Flask, and MySQL.*

## Overview

This is a Flask-based MySQL database designed to track a personal cosmetics collection.
It allows users to catalogue items, record purchases, and track usage.

This project serves two purposes:

1. **Personal use**: I use this app to maintain my own nail polish collection.

2. **Open source demo**: The code is available for others to explore or modify.

## Features

- Add and edit individual polish records with brand, type, color family, tags, and full descriptions
- Inline editing of polish fields (name, color, brand, etc.) with autocomplete
- Attach swatch photos and browse polishes with thumbnails
- Track usage logs with polish/tag relationships
- Server-side filtering by brand, color, polish type, tag, and destashed status
- Supports bulk data import and relational linking via custom scripts

## Tech Stack

- Python, Flask, SQLAlchemy
- MySQL: relational schema, enum fields, associations
- HTML, CSS, JavaScript (vanilla with fetch/datalist)

## Getting Started (*under construction*)

### 1. Clone the repository

In a terminal window, navigate to the directory where you would like to clone the repo. Then run the following:

```bash
git clone https://github.com/mbvillalonga/nail-polish-db.git
cd nail-polish-db
```

### 2. Set up a virtual environment

For Mac/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

For Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Database setup

#### 4a. Update environment variables

- Create your own .env file using the example:

```bash
cp .env.example .env
```

In your .env file, replace `your_username` and `your_password` with your own MySQL database credentials.

If necessary, also edit the `DB_HOST` and `DB_NAME` fields. Files are currently written to work with `localhost` and `nail_db`, respectively.

#### 4b. Create MySQL database (*under construction*)

## Project structure

Below is the file structure for the minimal working example:

```bash
nail-polish-db/
|-- app.py              # Main Flask app
|-- models.py           # Database tables specified as SQLAlchemy models
|-- setup_db.py         # Initializes database 
|-- migrations/         # Folder for Flask-Migrate files (auto-generated)
|-- templates/          # Folder for HTML templates
    |-- index.html      # Home page for displaying polishes
    |-- add.html        # Form to add new polish
    |-- add-mani.html   # Form to add new mani log entry
    |-- polishes.html   # List of all polishes
|-- static/             # For CSS/images for front end
|-- .env.example        # Template for credentials (see next step)
|-- venv/               # Virtual environment (not included in repo)
|-- requirements.txt    # Python dependencies
|-- README.md           # Documentation
```

## **Project Status**

### Overall Roadmap

1. Build app's structural skeleton (in progress)
2. Validate data flows (in progress)
3. Layer in UI structure
4. Add UX enhancements
5. Final styling

#### Completed

- Polish table with brand, color family, type, tags, and full description
- Add form for new polish records
- Inline editing for polish fields:
  - `name`, `full_desc`, `color_family`, and `brand`
  - Autocomplete enabled for `color_family` and `brand` (limited to existing brands only)
- Bulk import of swatch photo import with CSV-based path mapping
- Display thumbnails and lightbox views for swatches
- ManiLog table with date + polish associations
- Filtering by brand, color family, type, tag, and destashed flag in `polishes.html`
- CR of CRUD for `mani_logs`
  - `add_mani.html`: allows user to log a new manicure
  - Uses Select2 for autocomplete drop-down multi-select for polishes and tags
  - Can create a new tag with the Select2 drop-down as well
  - Added input fields for number of fingers and coats for each selected polish
- CRU of CRUD for `mani_photos`
  - Updated and renamed `import_swatch_photos.py` to `import_bulk_photos.py`
    - Script now takes arguments --file (full path to import list csv), --type (mani or polish), and -n (dry run - doesn't commit to database)
  - Running `import_bulk_photos.py` with `--type mani` will add mani photo paths to `nail_db.mani_photos` and link photo record to related record in `nail_db.mani_logs`

#### In Progress

- Full CRUD for `mani_logs` record creation
  - Future enhancements will include photo support (option to upload photos with an individual mani log record rather than in bulk)

- CRUD for image uploads (*e.g.*, item photos, usage photos)
  - Users will be able to upload images for each item (polish) or usage record (manicure) when creating record using Add form
  - Add form will create image directory and rename uploaded file(s) using database identifier(s)
  - Interface will support in-line uploading, if user wants to upload image after parent record creation
  - Image upload will create thumbnails for faster loading on main pages, reserving full-size for lightbox viewing

#### Planned

- Add optional photo upload fields to `add_polish.html` and `add_mani.html`
- Inline editing for `polish_type` (`polishes.html`, `app.py`)
- Tag adding/editing with multi-select support (`polishes.html`, `add.html`, `mani_logs.html`, `add_mani.html`)
- Collection stats/dashboard view (most-used tags, polish type breakdown, etc.)
- CSV export for polish and mani data
- Optional cloud storage migration for swatch photos
- Bulk import of usage photos (ManiPhoto) and order logs (OrderLog)
- Development of UI for Recipe and Ingredient tables
- Add/edit UI for OrderLog entries (date, vendor/item info, budgeting utilities)
- Add/edit UI for Recipe entries (ingredients, quantities, batch info)

## Screenshots (*under construction*)

## License (*under construction*)
