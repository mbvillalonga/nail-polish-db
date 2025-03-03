import datetime
from sqlalchemy import text
from models import db, app, Brand, Polish, OrderLog, ManiLog, SwatchPhoto, Ingredient, Recipe

# Use app context to access the database
with app.app_context():
    # Clear existing data (optional, for testing)
    # Disable foreign key checks temporarily 
    db.session.execute(text("SET FOREIGN_KEY_CHECKS=0;"))

    # Delete child table entries before parent tables
    db.session.execute(text("DELETE FROM polishes_order_logs;"))  # ✅ Clear many-to-many join table
    db.session.execute(text("DELETE FROM polishes_mani_logs;"))  # ✅ Clear join table for manicures
    db.session.execute(text("DELETE FROM ingredients_recipes;"))  # ✅ Clear recipe-ingredient links
    db.session.execute(text("DELETE FROM ingredients_order_logs;"))  # ✅ Clear ingredient orders

    # Delete parent records
    db.session.query(SwatchPhoto).delete()
    db.session.query(ManiLog).delete()
    db.session.query(OrderLog).delete()
    db.session.query(Polish).delete()
    db.session.query(Brand).delete()
    db.session.query(Ingredient).delete()
    db.session.query(Recipe).delete()
    db.session.commit()

    # Reset auto-increment counters
    db.session.execute(text("ALTER TABLE polishes AUTO_INCREMENT = 1;"))
    db.session.execute(text("ALTER TABLE brands AUTO_INCREMENT = 1;"))
    db.session.execute(text("ALTER TABLE order_logs AUTO_INCREMENT = 1;"))
    db.session.execute(text("ALTER TABLE mani_logs AUTO_INCREMENT = 1;"))
    db.session.execute(text("ALTER TABLE ingredients AUTO_INCREMENT = 1;"))
    db.session.execute(text("ALTER TABLE recipes AUTO_INCREMENT = 1;"))

    # Re-enable foreign key checks 
    db.session.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
    
    db.session.commit()

    print("Database cleared successfully.")

    # Add sample brands
    brand1 = Brand(name="Test Indie Brand", type="indie")
    brand2 = Brand(name="Mainstream Co.", type="mainstream")
    brand3 = Brand(name="Luxury Polish", type="luxury")
    db.session.add_all([brand1, brand2, brand3])
    db.session.commit()

    # Add sample polishes
    polish1 = Polish(name="Sunset Glow", brand_id=brand1.id, color_family="orange")
    polish2 = Polish(name="Moonlit Sky", brand_id=brand1.id, color_family="blue")
    polish3 = Polish(name="Gold Leaf Elegance", brand_id=brand2.id, color_family="gold")
    polish4 = Polish(name="Holo Magic", brand_id=brand3.id, color_family="silver")
    db.session.add_all([polish1, polish2, polish3, polish4])
    db.session.commit()

    # Add sample order logs
    order1 = OrderLog(order_date=datetime.date(2024, 3, 1), vendor="Polish Boutique", order_total=30.50)
    order2 = OrderLog(order_date=datetime.date(2024, 3, 15), vendor="Mainstream Store", order_total=15.99)
    order3 = OrderLog(order_date=datetime.date(2024, 3, 30), vendor="Mainstream Store", order_total=14.50)
    db.session.add_all([order1, order2, order3])
    db.session.commit()

    # Link orders to polishes (many-to-many)
    order1.polish.extend([polish1, polish2])
    order2.polish.append(polish3)
    order3.polish.append(polish4)
    db.session.commit()

    # Add sample manicure logs
    mani1 = ManiLog(mani_date=datetime.date(2024, 3, 10))
    mani2 = ManiLog(mani_date=datetime.date(2024, 3, 20))
    db.session.add_all([mani1, mani2])
    db.session.commit()

    # Link manicures to polishes (many-to-many)
    mani1.polish.extend([polish1, polish3, polish4])
    mani2.polish.append(polish2)
    db.session.commit()

    # Add sample swatch photos
    swatch1 = SwatchPhoto(path="static/images/sunset_glow_1.jpg", polish_id=polish1.id)
    swatch2 = SwatchPhoto(path="static/images/sunset_glow_2.jpg", polish_id=polish1.id)
    swatch3 = SwatchPhoto(path="static/images/moonlit_sky_1.jpg", polish_id=polish2.id)
    db.session.add_all([swatch1, swatch2, swatch3])
    db.session.commit()

    # Add sample ingredients
    ingredient1 = Ingredient(name="Holographic Pigment", vendor="Pigment Co.")
    ingredient2 = Ingredient(name="Gold Flakes", vendor="Supplies")
    ingredient3 = Ingredient(name="Base Coat Solution", vendor="Chem Lab")
    db.session.add_all([ingredient1, ingredient2, ingredient3])
    db.session.commit()

    # Add sample recipes
    recipe1 = Recipe(name="Holo Magic")
    recipe2 = Recipe(name="Gold Leaf Elegance")
    db.session.add_all([recipe1, recipe2])
    db.session.commit()

    # Link recipes to ingredients (many-to-many)
    recipe1.ingredient.extend([ingredient1, ingredient3])
    recipe2.ingredient.extend([ingredient2, ingredient3])
    db.session.commit()

    print("Sample data added successfully.")