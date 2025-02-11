# Database setup
# Uses MySQL

import os
import mysql.connector
from dotenv import load_dotenv
import subprocess

# Load environment variables from .env file
# See .env.example 
load_dotenv()

# Get MySQL credentials from env variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost") # default: localhost
DB_NAME = os.getenv("DB_NAME", "nail_db") # default: nail_db

# create_database(): establishes a MySQL connection, checks if the database exists, and creates it if not
def create_database():
    """Connects to MySQL and creates the database if it doesn't exist."""
    try: # connect to MySQL without specifying a database
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor() # create a cursor to execute SQL commands

        # create database using env variable if it does not exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
        print(f"Database '{DB_NAME}' is ready.")
        cursor.close() # close connection
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}") # print error message if database creation fails

# run_migrations(): run Flask-Migrate to apply table structures from models.py
def run_migrations():
    """Applies existing migrationes to the database using Flask-Migrate."""
    try:
        print("Running migrations...")
        # run the flask command to apply database migrations
        subprocess.run(["flask", "db", "upgrade"], check=True) 
        print("Migrations applied successfully.")
    except subprocess.CalledProcessError as err:
        print(f"Error applying migrations: {err}") # print error message if migrations fail

# Run script when executed directly
if __name__ == "__main__":
    create_database()
    run_migrations()