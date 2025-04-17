from sqlalchemy import text
from models import db, SwatchPhoto
from app import create_app

# Create the Flask app and push the app context
app = create_app()

with app.app_context():
    # Disable foreign key checks
    db.session.execute(text("SET FOREIGN_KEY_CHECKS=0;"))

    # Delete all records from swatch photos table
    db.session.query(SwatchPhoto).delete()
    db.session.commit()

    # Reset auto-increment counter for mani logs
    db.session.execute(text("ALTER TABLE swatch_photos AUTO_INCREMENT = 1;"))

    # Re-enable foreign key checks
    db.session.execute(text("SET FOREIGN_KEY_CHECKS=1;"))

    db.session.commit()
    print("Swatch photos reset successfully.")
