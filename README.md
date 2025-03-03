# nail-polish-db

*A relational database and GUI app for managing my nail polish collection*

## Overview

This is a Flask-based MySQL database designed to track a personal nail polish collection.
It allows users to log polishes, record purchases, and track usage.

This project serves two purposes:

1. **Personal use**: I use this app to maintain my own collection

2. **Open source demo**: The code is available for others to explore or modify

## Features

- Store and manage lists of polishes and brands
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
|-- static/             # For CSS/images for front end
|-- .env.example        # Template for credentials (see next step)
|-- venv/               # Virtual environment (not included in repo)
|-- requirements.txt    # Python dependencies
|-- README.md           # Documentation
```

## Available commands

**UNDER CONSTRUCTION**

## Future improvements

**UNDER CONSTRUCTION**

## Screenshots

**UNDER CONSTRUCTION**

## License

**UNDER CONSTRUCTION**
