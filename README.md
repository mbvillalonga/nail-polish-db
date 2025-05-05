# nail-polish-db

*An interactive web application for managing inventory, product photos, and usage logs in a structured database, built with Python, Flask, and MySQL.*

## Overview

This is a Flask-based MySQL database designed to track a personal cosmetics collection.
It allows users to catalogue items, record purchases, and track usage.

This project serves two purposes:

1. **Personal use**: I use this app to maintain my own nail polish collection.

2. **Open source demo**: The code is available for others to explore or modify.

## Features

- Store and manage lists of nail polishes and brands
- Store and manage lists of custom lacquer recipes and ingredients
- Record purchase history and track usage
- Web-based interface with an HTML front end using Flask
- SQLAlchemy ORM for managing a MySQL database
- Example scripts for querying and seeding data

## Installation

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

### Database Setup

#### Update environment variables

- Create your own .env file using the example:

```bash
cp .env.example .env
```

In your .env file, replace `your_username` and `your_password` with your own MySQL database credentials.

If necessary, also edit the `DB_HOST` and `DB_NAME` fields. Files are currently written to work with `localhost` and `nail_db`, respectively.

#### Create MySQL database

**UNDER CONSTRUCTION**

## Usage

**UNDER CONSTRUCTION**

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

## Available commands

**UNDER CONSTRUCTION**

## Future improvements

### Tags

- A table that stores tags used to categorize polishes, manicures, ingredients. Useful for filtering and grouping.
  - Added to models.py: 4/6/25
  - Added to app.py: 4/6/25

### Edit route and form

- Implement a way to edit individual records in the Flask app, in case of data entry errors.

### Polish list

- Tags for easy filtering by finish, colors, etc.: Create a many-to-many relationship (done: 4/6/25)
- Convert `color_family` attribute from string to single-select drop-down
- Add a destashed attribute

### Manicure log

- Include a way to specify type of manicure for accuracy of usage statistics

## Screenshots

**UNDER CONSTRUCTION**

## License

**UNDER CONSTRUCTION**
