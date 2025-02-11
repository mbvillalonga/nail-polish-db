# nail-polish-db

A relational database and GUI app for managing my nail polish collection

## File structure

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
|-- static/             # For CSS/images
|-- .env                # Database credentials (see .env.example)
|-- venv/               # Virtual environment (not included in repo)
|-- requirements.txt    # Python dependencies
|-- README.md           # Documentation
```

## Prerequisites

- Ensure MySQL is installed

- Install necessary Python dependencies

```bash
pip install flask flask-sqlalchemy flask-migrate flask-wtf python-dotenv
```

- Create your own .env file using the example:

```bash
cp .env.example .env
```

In your .env file, replace `your_username` and `your_password` with your own MySQL database credentials.

If necessary, also edit the `DB_HOST` and `DB_NAME` fields. Files are currently written to work with `localhost` and `nail_db`, respectively.

## Database Setup

### Update environment variables

### Create MySQL database

To create the MySQL database and apply Flask migrations, run:

```bash
python setup_db.py
```
