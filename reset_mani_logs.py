from sqlalchemy import text
from models import db, app, ManiLog

with app.app_context():
    # Disable foreign key checks
    db.session.execute(text("SET FOREIGN_KEY_CHECKS=0;"))

    # Clear association table between polishes and mani logs
    db.session.execute(text("DELETE FROM polishes_mani_logs;"))

    # Delete all records from mani logs table
    db.session.query(ManiLog).delete()
    db.session.commit()

    # Reset auto-increment counter for mani logs
    db.session.execute(text("ALTER TABLE mani_logs AUTO_INCREMENT = 1;"))

    # Re-enable foreign key checks
    db.session.execute(text("SET FOREIGN_KEY_CHECKS=1;"))

    db.session.commit()
    print("Mani logs and associations reset successfully.")
