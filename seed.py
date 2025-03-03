from models import db, app, Brand, Polish

# Use app context to access the database
with app.app_context():
    # Delete existing data (optional, for testing)
    db.session.query(Polish).delete()
    db.session.query(Brand).delete()

    # Add sample brands
    brand1 = Brand(name="Test Indie Brand", type="indie")
    brand2 = Brand(name="Sample Luxury Brand", type="luxury")
    db.session.add_all([brand1, brand2])
    db.session.commit()

    # Add sample polishes
    polish1 = Polish(name="Sunset Glow", brand_id=brand1.id, color_family="orange")
    polish2 = Polish(name="Moonlit Sky", brand_id=brand2.id, color_family="blue")
    db.session.add_all([polish1, polish2])
    db.session.commit()

    print("Sample data added successfully.")