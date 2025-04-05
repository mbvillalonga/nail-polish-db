from sqlalchemy import text
from models import db, app, Brand, Recipe, Polish, ManiLog, ManiPhoto, SwatchPhoto, OrderLog, Ingredient

with app.app_context():
    # Disable foreign key checks
    db.session.execute(text("SET FOREIGN_KEY_CHECKS=0;"))

    # List of association tables (many-to-many links)
    association_tables = [
        "polishes_order_logs",
        "polishes_mani_photos",
        "polishes_mani_logs",
        "ingredients_recipes",
        "ingredients_order_logs",
    ]

    # List of main tables to clear
    models = [Brand, Recipe, Polish, SwatchPhoto, ManiPhoto, OrderLog, ManiLog, Ingredient]

    # Clear association tables first
    for table in association_tables:
        db.session.execute(text(f"DELETE FROM {table};"))

    # Delete all records from main tables
    for model in models:
        db.session.query(model).delete()
    db.session.commit()

    # Reset auto-increment counters
    for model in models:
        table_name = model.__tablename__  # Get table name from model
        db.session.execute(text(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1;"))

    # Re-enable foreign key checks
    db.session.execute(text("SET FOREIGN_KEY_CHECKS=1;"))

    db.session.commit()
    print("Database reset successfully.")
